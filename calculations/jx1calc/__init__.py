"""JX1 engineering calculation package.

Modules
-------
design      load the design point YAML and derive link masses / inertias
mjcf        generate the parametric MuJoCo analysis model (not the CAD-derived sim model)
kinematics  closed-form 6-DOF leg inverse kinematics (hip Y-R-P, knee, ankle P-R)
lipm        linear-inverted-pendulum ZMP preview control
gait        footstep planning, swing trajectories, whole-body trajectory synthesis
invdyn      floating-base inverse dynamics with contact-wrench distribution
ankle       parallel (two push-rod) ankle mapping between joint and motor space
"""
