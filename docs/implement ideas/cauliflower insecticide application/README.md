1. Context & Key Parameters
Crop & Geometric Specifications

    Crop: Cauliflower at approximately 50% of its growth cycle (mid-stage development).

    Foliage & Crop Volume: Substantial leaf development is already present. The crop forms a raised physical obstacle under the robot chassis/axle, causing light contact with lower structural components.

    In-Row Plant Spacing: 40 cm.

    Inter-Row Spacing: 40 cm.

    Soil Condition: Bare soil between rows and individual plants.

    Clearance: Cauliflower plants pass centrally and unobstructed beneath the main robot frame and wheel axles.

2. System Architecture & Mechanical Design
A. Fluid Supply & Reservoir (Top-Mounted)

    On-Board Tank: Centrally mounted on the chassis to maintain optimal weight distribution. Equipped with a fill opening, air breather, and optional low-level fluid sensor to prevent dry running.

    Fluid Line Routing: Liquid flows via gravity feed or a dedicated metering pump down from the tank to the lower attachment.

B. Mounting & Suspension Frame (Bottom-Mounted)

    Ground-Following Mechanism: To compensate for soil unevenness and wheel ruts, the attachment utilizes a contour-following suspension (e.g., a parallelogram linkage or dedicated depth-control trailing wheel per row). This ensures the application nozzles maintain a constant working height relative to the root crown.

    Crop Guidance System: Given the size of mid-stage cauliflower leaves, smooth, angled crop deflectors or flexible guide bars are integrated into the frame. These gently nudge side leaves away, preventing nozzles from catching or damaging plant tissue.

3. Precision Application System
A. Root Crown Target Positioning

    Application Point: Positioned on both sides of the root crown (approx. 3 to 5 cm laterally from the main stem).

    Delivery Method: Two flexible drop hoses/spray nozzles per crop row, angled downward and inward toward the soil surface.

    Drift & Waste Reduction: By depositing liquid close to the soil surface right at the stem base, evaporative loss and foliage contamination are minimized.

B. Detection & Pulsed Micro-Dosing

To maximize liquid efficiency, the application is delivered via targeted pulses rather than a continuous stream:

    Triggering Options:

        Sensor-Based: Optical, LiDAR, camera, or ultrasonic sensors identify the centerline of the cauliflower stem or plant canopy.

        Distance-Based (Wheel Encoder): Because plants are spaced at fixed 40 cm intervals, wheel rotation/odometry triggers doses precisely every 40 cm.

    Actuation: Fast-acting solenoid valves mounted near the hose ends open for a short, adjustable burst (e.g., 50–100 ms) as the root crown passes beneath.

4. Operational Workflow

    Approach: The robot straddles the row. The cauliflower passes freely under the wheelbase and chassis height.

    Foliage Deflection: Integrated guide bars gently push outer leaves away from the target zone.

    Detection Signal: A sensor or wheel encoder registers that the root crown is in position beneath the nozzles.

    Pulsed Injection: Left and right solenoid valves fire simultaneously, injecting a precise volume of liquid onto the soil directly adjacent to the root.

    Cycle Repeat: Valves close immediately, and the controller tracks the next 40 cm increment to the following plant.

5. Key Engineering Considerations

    Under-Chassis Clearance: Minimum vertical clearance under the robot chassis must accommodate mid-stage cauliflowers (typically 25–35 cm).

    Soil & Debris Protection: Because drop nozzles operate close to the ground, shielding is required to prevent clogging from splash-back, mud, and crop residue.

    Adjustability: Lateral spacing (left/right of the stem) and nozzle application angles should be easily adjustable to adapt to different growth stages.