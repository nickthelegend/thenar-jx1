# JX1 in NVIDIA Isaac Sim / Isaac Lab

Isaac Sim is not installed on the design machine, so the USD has **not** been generated or tested here (UNVERIFIED).
The asset path is the CAD-derived URDF, which Isaac's URDF importer converts to USD:

1. Build the ROS 2 package or copy `ros2_ws/src/jx1_description` (URDF + `meshes/`).
2. Isaac Sim 4.x/5.x → *File → Import → URDF* with `import_config.yaml` settings, or run
   `./python.sh simulation/isaac/import_jx1.py` from the Isaac Sim directory.
3. Isaac Lab: point an `ArticulationCfg` at the generated `jx1.usd`; actuator limits come from `import_config.yaml`
   (effort/velocity per joint are already in the URDF `<limit>` tags).

The parallel ankle is modelled as serial pitch → roll joints (as Unitree G1 does in `unitree_rl_gym`); motor-space
conversion uses `calculations/jx1calc/ankle.py`.
