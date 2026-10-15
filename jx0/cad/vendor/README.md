# Vendor servo model

`STS3215_SO-ARM100.stl`: the Feetech STS3215 with both horns, from TheRobotStudio's SO-ARM100 / SO-101 arm
(`Simulation/SO101/assets/sts3215_03a_v1.stl`, https://github.com/TheRobotStudio/SO-ARM100), licensed Apache-2.0.
Binary STL in metres, unchanged. `jx0/verify/verify_fit.py` checks every printed part against it as a second opinion to
the servo model in `geometry.servo_st()`. To get our servo frame: scale ×1000, then x = 12.5 − X, y = −Y, z = Z.

`geometry.servo_st()` is the larger of this model and Feetech's own factory model (the ST3215 STEP that Waveshare
distributes on its wiki, https://www.waveshare.com/wiki/ST3215_Servo). That STEP is not redistributed here. The values
taken from it:
- the rear-face case holes: Ø1.6, 2.9 mm deep, at x 8.3 / 32.75, y ±10.25;
- the cable sockets' opening: x 11.4–16.7, |y| ≤ 10, the plugs inside the case;
- the output band top at z 15.9 and the raised strip to z 17.45;
- the passive horn face at z −17.75.

They agree with the Feetech ST-3215-C018 datasheet's outline drawing.
