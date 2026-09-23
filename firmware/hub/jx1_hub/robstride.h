// RobStride private CAN protocol (CAN 2.0B, 1 Mbit/s, 29-bit extended ID) — encoder/decoder.
// Source (VERIFIED): RobStride RS00/RS02/RS03/RS04/RS06 user manuals rev. 260713, section 4.1
//   ID bits 28..24 = communication type, bits 23..8 = data area 2, bits 7..0 = destination CAN ID.
//   Type 1 (operation control): ID[23:8] = torque ff (uint16 over +-T_MAX); data: angle(+-4pi), velocity(+-V_MAX),
//                               Kp (0..KP_MAX), Kd (0..KD_MAX) — each uint16, big-endian.
//   Type 2 (feedback): ID[23:22] mode, ID[21:16] faults, ID[15:8] motor ID, ID[7:0] host ID;
//                      data: angle, velocity, torque (uint16 big-endian, same ranges), temperature*10 (uint16).
//   Type 3 enable, type 4 stop (data[0]=1 clears faults), type 6 set mechanical zero (data[0]=1),
//   type 18 single-parameter write (CAN_TIMEOUT: 20000 = 1 s).
#pragma once
#include <stdint.h>

namespace robstride {

enum Model : uint8_t { RS00 = 0, RS02, RS03, RS04, RS06 };

struct Scale { float t_max, v_max, kp_max, kd_max; };
// torque / velocity / Kp ranges VERIFIED from each model's manual; Kd max VERIFIED for RS03/RS04/RS06 (100),
// ASSUMED 5.0 for RS00/RS02 pending confirmation (open issue: verify before first enable).
static const Scale SCALE[] = {
  /* RS00 */ {14.0f, 33.0f, 500.0f, 5.0f},
  /* RS02 */ {17.0f, 44.0f, 500.0f, 5.0f},
  /* RS03 */ {60.0f, 20.0f, 5000.0f, 100.0f},
  /* RS04 */ {120.0f, 15.0f, 5000.0f, 100.0f},
  /* RS06 */ {36.0f, 50.0f, 5000.0f, 100.0f},
};
static const float P_MAX = 12.566370614f;  // 4*pi

enum Type : uint8_t { GET_ID = 0, CONTROL = 1, FEEDBACK = 2, ENABLE = 3, STOP = 4, SET_ZERO = 6, SET_CAN_ID = 7,
                      PARAM_READ = 17, PARAM_WRITE = 18, FAULT = 21 };

inline uint16_t f2u(float x, float lo, float hi) {
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return (uint16_t)((x - lo) * 65535.0f / (hi - lo) + 0.5f);
}
inline float u2f(uint16_t u, float lo, float hi) { return lo + (hi - lo) * (float)u / 65535.0f; }

inline uint32_t make_id(uint8_t type, uint16_t data2, uint8_t dest) {
  return ((uint32_t)(type & 0x1F) << 24) | ((uint32_t)data2 << 8) | dest;
}

struct Frame { uint32_t id; uint8_t len; uint8_t buf[8]; };

// MIT-style operation control: tau = Kp*(q_des - q) + Kd*(dq_des - dq) + tau_ff  (evaluated inside the actuator)
inline Frame control(Model m, uint8_t motor_id, float q, float dq, float kp, float kd, float tau_ff) {
  const Scale &s = SCALE[m];
  Frame f;
  f.id = make_id(CONTROL, f2u(tau_ff, -s.t_max, s.t_max), motor_id);
  f.len = 8;
  uint16_t a = f2u(q, -P_MAX, P_MAX), v = f2u(dq, -s.v_max, s.v_max), p = f2u(kp, 0, s.kp_max), d = f2u(kd, 0, s.kd_max);
  f.buf[0] = a >> 8; f.buf[1] = a & 0xFF; f.buf[2] = v >> 8; f.buf[3] = v & 0xFF;
  f.buf[4] = p >> 8; f.buf[5] = p & 0xFF; f.buf[6] = d >> 8; f.buf[7] = d & 0xFF;
  return f;
}

inline Frame simple(Type t, uint8_t host_id, uint8_t motor_id, uint8_t b0 = 0) {
  Frame f;
  f.id = make_id(t, (uint16_t)host_id, motor_id);
  f.len = 8;
  for (int i = 0; i < 8; i++) f.buf[i] = 0;
  f.buf[0] = b0;
  return f;
}

struct State { uint8_t motor_id, mode, faults; float q, dq, tau, temp_c; bool valid; };

inline bool is_feedback(uint32_t id) { return ((id >> 24) & 0x1F) == FEEDBACK; }

inline State decode_feedback(Model m, uint32_t id, const uint8_t *b) {
  const Scale &s = SCALE[m];
  State st;
  st.motor_id = (id >> 8) & 0xFF;
  st.faults = (id >> 16) & 0x3F;   // bit5 uncalibrated, bit4 stall overload, bit3 encoder, bit2 over-temp, bit1 over-current, bit0 under-voltage
  st.mode = (id >> 22) & 0x03;     // 0 reset, 1 calibration, 2 run
  st.q = u2f((uint16_t)(b[0] << 8 | b[1]), -P_MAX, P_MAX);
  st.dq = u2f((uint16_t)(b[2] << 8 | b[3]), -s.v_max, s.v_max);
  st.tau = u2f((uint16_t)(b[4] << 8 | b[5]), -s.t_max, s.t_max);
  st.temp_c = (float)(uint16_t)(b[6] << 8 | b[7]) / 10.0f;
  st.valid = true;
  return st;
}

}  // namespace robstride
