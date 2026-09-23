// JX1 real-time CAN hub — Teensy 4.1 (3 CAN controllers), one of two hubs (HUB_ID 0 = A, 1 = B).
// Responsibilities (docs/architecture.md): deterministic 500 Hz bus schedule, host-command interpolation, state
// aggregation, soft joint limits, current/temperature limits, host + CAN watchdogs, E-stop monitoring, fault latching.
// Build: Teensyduino + FlexCAN_T4. Status: DESIGN CODE — compiles against FlexCAN_T4 API, NOT yet tested on hardware.
#include <FlexCAN_T4.h>
#include "robstride.h"
#include "config.h"

using namespace robstride;

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can1;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> can2;
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> can3;

struct Target { float q, dq, kp, kd, tau; };
Target tgt_prev[NJ], tgt_next[NJ];
State state[NJ];
uint32_t last_fb_us[NJ];
uint32_t host_last_us = 0, host_period_us = 20000, host_seq = 0;
bool estop = false, latched_fault = false, enabled = false;

enum HubMode : uint8_t { DISABLED = 0, DAMPING = 1, RUN = 2 };
HubMode mode = DISABLED;

static void send(uint8_t bus, const Frame &f) {
  CAN_message_t m;
  m.id = f.id; m.flags.extended = 1; m.len = f.len;
  for (int i = 0; i < 8; i++) m.buf[i] = f.buf[i];
  if (bus == 0) can1.write(m); else if (bus == 1) can2.write(m); else can3.write(m);
}

static void on_rx(const CAN_message_t &m) {
  if (!m.flags.extended || !is_feedback(m.id)) return;
  uint8_t mid = (m.id >> 8) & 0xFF;
  for (int j = 0; j < NJ; j++) {
    if (JOINTS[j].can_id == mid && JOINTS[j].bus == m.bus - 1) {
      state[j] = decode_feedback(JOINTS[j].model, m.id, m.buf);
      last_fb_us[j] = micros();
      if (state[j].faults) latched_fault = true;
      return;
    }
  }
}

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

// joint-space command -> actuator command (sign, zero offset, soft limits, temperature derating)
static Frame command_for(int j, float alpha) {
  const JointCfg &c = JOINTS[j];
  Target t;
  t.q = tgt_prev[j].q + alpha * (tgt_next[j].q - tgt_prev[j].q);
  t.dq = tgt_next[j].dq; t.kp = tgt_next[j].kp; t.kd = tgt_next[j].kd; t.tau = tgt_next[j].tau;
  t.q = clampf(t.q, c.q_min + SOFT_MARGIN, c.q_max - SOFT_MARGIN);
  float tmax = c.tau_limit;
  if (state[j].valid && state[j].temp_c > TEMP_DERATE_C) tmax *= clampf((TEMP_STOP_C - state[j].temp_c) / (TEMP_STOP_C - TEMP_DERATE_C), 0.f, 1.f);
  t.tau = clampf(t.tau, -tmax, tmax);
  if (mode != RUN) { t.kp = 0; t.dq = 0; t.tau = 0; t.kd = DAMPING_KD; t.q = state[j].valid ? c.sign * (state[j].q - c.zero) : 0; }
  // joint -> motor frame
  float qm = c.sign * t.q + c.zero, dqm = c.sign * t.dq, taum = c.sign * t.tau;
  return control(c.model, c.can_id, qm, dqm, t.kp, t.kd, taum);
}

// ------------------------------------------------------------------ host protocol (USB serial, little-endian)
// host -> hub: 0xA5 0x5A, seq(u32), mode(u8), NJ x {q,dq,kp,kd,tau}(5 x f32), crc16
// hub -> host: 0x5A 0xA5, seq(u32), flags(u8), NJ x {q,dq,tau,temp}(4 x f32) + faults(u8), crc16
static uint16_t crc16(const uint8_t *d, size_t n) {
  uint16_t c = 0xFFFF;
  for (size_t i = 0; i < n; i++) { c ^= d[i]; for (int k = 0; k < 8; k++) c = (c & 1) ? (c >> 1) ^ 0xA001 : c >> 1; }
  return c;
}

static void poll_host() {
  static uint8_t buf[8 + NJ * 20 + 2];
  static size_t n = 0;
  while (Serial.available()) {
    uint8_t b = Serial.read();
    if (n == 0 && b != 0xA5) continue;
    if (n == 1 && b != 0x5A) { n = 0; continue; }
    buf[n++] = b;
    if (n == sizeof(buf)) {
      n = 0;
      uint16_t c = buf[sizeof(buf) - 2] | (buf[sizeof(buf) - 1] << 8);
      if (crc16(buf, sizeof(buf) - 2) != c) continue;
      memcpy(&host_seq, buf + 2, 4);
      uint8_t req = buf[6];
      for (int j = 0; j < NJ; j++) { tgt_prev[j] = tgt_next[j]; memcpy(&tgt_next[j], buf + 8 + j * 20, 20); }
      uint32_t now = micros();
      host_period_us = constrain(now - host_last_us, 5000, 40000);
      host_last_us = now;
      if (!estop && !latched_fault && req == RUN) mode = RUN; else if (req == DAMPING) mode = DAMPING;
    }
  }
}

static void send_state() {
  static uint8_t out[7 + NJ * 17 + 2];
  out[0] = 0x5A; out[1] = 0xA5; memcpy(out + 2, &host_seq, 4);
  out[6] = (estop << 0) | (latched_fault << 1) | ((uint8_t)mode << 2);
  for (int j = 0; j < NJ; j++) {
    const JointCfg &c = JOINTS[j];
    float v[4] = {c.sign * (state[j].q - c.zero), c.sign * state[j].dq, c.sign * state[j].tau, state[j].temp_c};
    memcpy(out + 7 + j * 17, v, 16);
    out[7 + j * 17 + 16] = state[j].faults | ((micros() - last_fb_us[j] > CAN_TIMEOUT_US) << 7);
  }
  uint16_t c = crc16(out, sizeof(out) - 2);
  out[sizeof(out) - 2] = c & 0xFF; out[sizeof(out) - 1] = c >> 8;
  Serial.write(out, sizeof(out));
}

void setup() {
  pinMode(ESTOP_PIN, INPUT_PULLUP);  // NC E-stop contact to GND: HIGH = pressed / wire broken (fail-safe)
  Serial.begin(0);                   // native USB 480 Mbit/s
  can1.begin(); can1.setBaudRate(1000000); can1.enableFIFO(); can1.enableFIFOInterrupt(); can1.onReceive(on_rx);
  can2.begin(); can2.setBaudRate(1000000); can2.enableFIFO(); can2.enableFIFOInterrupt(); can2.onReceive(on_rx);
  can3.begin(); can3.setBaudRate(1000000); can3.enableFIFO(); can3.enableFIFOInterrupt(); can3.onReceive(on_rx);
  delay(200);
  for (int j = 0; j < NJ; j++) {  // stop, clear faults, then enable into damping (no motion until host sends RUN)
    send(JOINTS[j].bus, simple(STOP, HOST_CAN_ID, JOINTS[j].can_id, 1));
    delayMicroseconds(300);
    send(JOINTS[j].bus, simple(ENABLE, HOST_CAN_ID, JOINTS[j].can_id));
    delayMicroseconds(300);
  }
  mode = DAMPING;
}

void loop() {
  static uint32_t tick = micros();
  can1.events(); can2.events(); can3.events();
  poll_host();
  estop = digitalRead(ESTOP_PIN) == HIGH;
  if (estop || latched_fault || (micros() - host_last_us > HOST_TIMEOUT_US)) mode = (mode == DISABLED) ? DISABLED : DAMPING;
  if ((int32_t)(micros() - tick) < (int32_t)BUS_PERIOD_US) return;
  tick += BUS_PERIOD_US;
  float alpha = constrain((float)(micros() - host_last_us) / host_period_us, 0.f, 1.f);
  for (int j = 0; j < NJ; j++) send(JOINTS[j].bus, command_for(j, alpha));   // <= 3 joints per bus -> ~45 % load
  static uint8_t div = 0;
  if (++div >= STATE_DIV) { div = 0; send_state(); }
}
