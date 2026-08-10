TITLE: AgriRover: A Low-Cost Autonomous Ground Robot for Targeted Agrochemical Dosing and In-Situ Soil Diagnostics on Indian Smallholdings

SUBTITLE: Design, Embedded Safety Architecture and Pre-Field Software Validation

AUTHORS: Vivek Kumar Gupta (corresponding author) | Kapadiya Hitanshu Mukeshbhai | Shreyash Wagh | Pritish Nandy

AFFILIATION: Department of Mechanical Engineering, Indian Institute of Technology Bombay, Powai, Mumbai 400076, Maharashtra, India (V. K. Gupta, K. H. Mukeshbhai, S. Wagh); Department of Aerospace Engineering, Indian Institute of Technology Bombay (P. Nandy)

CONTACT: Corresponding author e-mail: 25b2269@iitb.ac.in

VENUE: Submitted as a full-length paper to the 38th National Convention of Agricultural Engineers, The Institution of Engineers (India)

ABSTRACT:
Indian smallholders apply agrochemicals almost entirely by blanket spraying, because per-plant decision-making is not economically available to a farmer cultivating one to five acres. The consequence is measurable on three axes at once: chemical is wasted on healthy plants, the operator is exposed to the spray cloud for the whole duration of the pass, and no spatial record of the intervention survives the season. This paper presents AgriRover, a differential-drive ground robot designed to close that gap at a hardware cost of Rs 41,150, by combining on-board vision-based weed and disease detection, a needle-injection dosing head that treats individual plants, and a seven-parameter soil probe read over Modbus RTU. The contribution of this paper is not a yield claim; it is an engineering account of how a machine that autonomously carries chemical through a standing crop can be made safe, auditable and affordable using commodity components. We describe a three-tier architecture that deliberately separates hard real-time actuation on an ESP32 running FreeRTOS from soft real-time perception on a Raspberry Pi 5, and we present the safety design in full: a nine-bit FreeRTOS event group whose drive-inhibit mask is defined once in a single header, a latching mechanical emergency stop wired to the microcontroller enable pin so that no software element can override it, a 1500 ms dead-man timeout on the command link, and HMAC-SHA256 authentication with a monotonic replay counter on every motion command. We then report what has actually been verified. A 147-test Python suite passes across ten modules; a closed-loop kinematic simulation of a 20 m by 30 m plot shows that the extended Kalman filter reduces localisation root-mean-square error from 17.893 m under dead reckoning and 2.256 m under raw GNSS to 0.943 m, and reduces root-mean-square cross-track error during row following from 13.817 m to 0.563 m, which is the difference between a machine that leaves the row and one that stays inside a 0.60 m row corridor. We are explicit that the physical rover is not yet built, that no field trial has been run, and that every agronomic figure in the paper is stated as a validation gate rather than a result. We close with the six-gate acceptance protocol -- bench, tethered, plot and multi-week field stages -- that the project must pass before any efficacy claim is made, and we argue that publishing the protocol before the data is the honest order in which agricultural robotics for smallholders should be reported.

KEYWORDS: agricultural robotics; precision agriculture; targeted spraying; embedded safety architecture; FreeRTOS; extended Kalman filter; smallholder mechanisation; edge inference

# 1. Introduction

## 1.1 The smallholder decision gap

Indian agriculture is dominated by small and marginal operational holdings. For a farmer cultivating between one and five acres, the economics of crop protection are unforgiving in a specific way: the cost of deciding is larger than the cost of not deciding. Determining which plants in a field actually carry a fungal lesion, and treating only those, requires either labour that the farm cannot afford or instrumentation that the farm cannot buy. Blanket spraying is therefore not an error of judgement but a rational response to an absent tool. The farmer walks the field with a knapsack sprayer, treats every plant identically, and accepts the waste as the price of certainty.

The costs of that response are, however, real and they compound. Chemical applied to asymptomatic plants is a direct input loss. The operator carrying an open sprayer through a standing crop is exposed to drift for the entire duration of the pass, typically without respiratory protection. Repeated uniform application across seasons drives resistance in target pest populations. And because the intervention is undocumented, the farm accumulates no spatial history that could inform the following season, qualify the produce for a buyer with residue requirements, or support a claim under a scheme that rewards reduced chemical use.

Precision agriculture answers all four of these problems in principle, and has answered them in practice on large holdings for two decades. The obstacle for the Indian smallholding is not conceptual but dimensional. Commercial variable-rate and see-and-spray equipment is designed to be amortised over hundreds of hectares, is sized for tractor mounting, and carries a capital cost one to two orders of magnitude above what a five-acre farm can service. A tool that is correct in principle and unbuyable in practice does not change the farmer's decision.

## 1.2 Design position

AgriRover is an attempt to place a per-plant decision-making machine inside the smallholder's capital envelope. The design position that follows from that constraint can be stated in four commitments.

First, cost is a hard design constraint and not an optimisation target. The bill of materials is fixed at Rs 41,150 using components available from Indian retail supply, and every subsystem choice in this paper was made under that ceiling. Where a more capable component exists, we record it as an upgrade path rather than adopting it.

Second, the machine must decide per plant, not per pass. This forces on-board perception, because a design that transmits imagery to a server for classification fails in the connectivity conditions of the fields it is meant to serve.

Third, safety must be architectural rather than procedural. A machine that carries agrochemical, drives autonomously through a crop, and operates near people cannot rely on correct software to be safe. The emergency stop path in this design is mechanical and cuts the microcontroller enable pin directly; the drive-inhibit logic is defined exactly once in a single header so that no subsystem can hold a divergent view of whether motion is permitted.

Fourth, and least conventionally, the machine must be auditable. Every dose is recorded with its position, its trigger, and the confidence of the detection that caused it. The rationale is commercial as much as agronomic: a smallholder's route to a price premium runs through a buyer who wants evidence, and evidence is a data product.

## 1.3 Contribution and honest scope

This paper contributes: a complete three-tier architecture for a low-cost agricultural robot with an explicit real-time boundary; a safety architecture in which the drive-inhibit condition is a single centrally defined mask consumed by every actuating task; a security design for the command link appropriate to an untrusted wireless environment; and a quantified pre-field validation of the navigation and perception software, including a closed-loop simulation that isolates the contribution of sensor fusion to row-following accuracy.

We are equally explicit about what this paper is not. The physical rover has not been assembled. No field trial has been conducted. No agronomic efficacy has been measured. Every number in this paper is either a software test result, a simulation result under a stated model, or a design target that we identify as such. Section 10 states the six acceptance gates that the project must pass before any claim about chemical reduction, detection accuracy in the field, or yield effect is made. We take the view that in agricultural robotics, where unvalidated efficacy claims are common and expensive to the farmer who acts on them, publishing the acceptance protocol before the data is the correct order of reporting.

# 2. Related Work and State of the Art

## 2.1 Targeted spraying

Machine-vision-guided selective spraying is an established field. Systems in commercial use on large holdings identify weeds against a crop background in real time and actuate individual nozzles, achieving substantial reductions in herbicide volume relative to broadcast application. The engineering that makes these systems work -- high frame-rate imaging, tightly calibrated nozzle timing, and vehicle speed control -- is well documented. What is not transferable is the cost structure: these are tractor-mounted implements whose sensing and actuation hardware alone exceeds the total capital available to a smallholder.

A second body of work addresses small autonomous platforms for horticulture and greenhouse use, where the vehicle is small, slow, and operates in a structured environment. These platforms demonstrate that per-plant intervention is achievable on a small chassis. Their limitation for our purpose is that structured environments supply localisation aids -- rails, fiducials, reliable row geometry -- that an Indian smallholding does not.

AgriRover sits between these: an unstructured outdoor field, a smallholder cost envelope, and per-plant actuation. The consequence of occupying that position is that we cannot buy accuracy, so we must compute it, which is why sensor fusion rather than sensor quality is the central navigation contribution of this work.

## 2.2 Soil diagnostics

Soil nutrient status on Indian smallholdings is typically assessed, if at all, by periodic laboratory testing of composite samples, with turnaround measured in weeks and spatial resolution equal to the whole field. Capacitive and electrochemical probes that report moisture, temperature, electrical conductivity, pH and available nitrogen, phosphorus and potassium over an industrial fieldbus have become inexpensive enough to mount on a small vehicle. The relevant engineering question is no longer whether such a probe can be read, but whether readings taken in motion, at unknown insertion depth, in variable soil moisture, are stable enough to support a prescription. We treat this as an open question and design the probe interface around it: the rover inserts the probe with a linear actuator at a commanded depth while stationary, and Gate 3 in Section 10 is specifically a probe repeatability gate.

## 2.3 Edge inference on constrained hardware

The feasibility of the whole design rests on running a detection network at a useful frame rate on a single-board computer with a power budget of a few watts. Quantised single-stage detectors on 8-bit integer arithmetic, executed either on a neural accelerator or on the CPU through a delegated runtime, are now the standard approach. Our design keeps two backends behind one interface for a reason that is operational rather than technical: accelerator availability in Indian retail supply is inconsistent, and a design that hard-depends on a specific accelerator is a design that cannot be built in the month it is needed.

# 3. Design Requirements and Constraints

The requirements below were derived from the operating context described in Section 1 and were treated as binding during design. Table 1 states them with the design response and the mechanism by which each is verified.

TABLE:
Requirement | Design response | Verification mechanism
Hardware cost at or below Rs 45,000 | Fixed BOM of Rs 41,150; commodity ESP32 and Raspberry Pi 5; no proprietary implement | Costed BOM, Section 9
Per-plant decision without connectivity | Quantised detector executed on board; dual accelerator/CPU backend behind one interface | Bench inference benchmark, Gate 2
Operate inside a 0.60 m row corridor | EKF fusion of GNSS, wheel odometry and IMU; boustrophedon planner with pure-pursuit guidance | Closed-loop simulation, Section 8; Gate 4
No software element may defeat the stop | Latching mechanical E-stop on ESP32 enable pin; relay coils de-energised at boot | Bench interlock test, Gate 1
Motion must halt on loss of supervision | 1500 ms command dead-man; EVT_LINK_LOST in drive-inhibit mask | Firmware unit test; bench link-cut test
Command link must resist spoofing and replay | HMAC-SHA256 truncated to 128 bits; monotonic counter in NVS; lockout after 8 failures | Firmware unit test; Section 7
Every intervention must be auditable | Per-dose record with position, trigger and confidence; ISO 11783-10 export | Software test suite, Section 8.4
Buildable by an undergraduate team | Off-the-shelf modules, no custom silicon, documented bring-up checklist | Hardware bring-up checklist in repository

# 4. System Architecture

## 4.1 Three-tier decomposition and the real-time boundary

The architecture separates three concerns that have incompatible timing requirements. Figure 1 shows the decomposition.

FIG: fig1_architecture.png | Three-tier system architecture. The horizontal rule between the Raspberry Pi 5 and the ESP32 is the real-time boundary: everything below it is hard real-time and safety-relevant, everything above it is soft real-time and may be preempted, delayed or restarted without compromising machine safety. The independent safety path at the base is electrically outside both tiers.

The lower tier is an ESP32 running FreeRTOS. It owns every actuator, every safety interlock, and the soil probe fieldbus. Its tasks are periodic with deadlines in the tens of milliseconds, and its correctness requirement is that it must fail safe under any fault, including total loss of the tier above it.

The middle tier is a Raspberry Pi 5 running the perception pipeline, the extended Kalman filter, the mission scheduler and the data layer. Its work is computationally heavy, latency-tolerant, and explicitly not trusted with safety. If this tier crashes, the lower tier stops the machine within 1500 ms because signed commands cease to arrive.

The upper tier is the operator interface: a Telegram bot for field use, where a farmer already has the application installed and needs no new device, and a web dashboard for review. This tier can issue a remote stop request but cannot suppress one.

Placing the real-time boundary here has a consequence worth stating plainly: no amount of failure in the perception or planning software can cause an unsafe actuation, because the tier that actuates does not accept unsigned instructions and stops when instructions stop.

## 4.2 Inter-tier transport

The Pi and ESP32 communicate over a serial link at 115200 baud with an MQTT path available for telemetry and for supervisory commands. Motion and dosing commands carry an authentication tag and a sequence counter as described in Section 7. Telemetry -- soil probe frames, GNSS fixes, status, and alerts -- flows upward on separate topics per rover identifier, so that a multi-rover deployment requires no change to the message format.

# 5. Mechanical and Electrical Subsystem

## 5.1 Chassis and drive

The platform is a differential-drive four-wheel chassis sized to pass between crop rows at 0.60 m spacing. Drive is through two BTS7960 half-bridge modules, one per side, giving independent speed and direction control with current sensing. Wheel encoders close a velocity loop implemented as a proportional-integral-derivative controller, which serves two purposes: it holds commanded ground speed across the varying rolling resistance of field soil, and it supplies the odometry that the navigation filter consumes.

The choice of differential drive over Ackermann steering was made for turning radius. A boustrophedon coverage pattern in a small plot spends a significant fraction of its path length in headland turns, and a skid-steer platform can reverse direction within the row width, which an Ackermann platform cannot.

## 5.2 Dosing head

Targeted application uses a needle-injection head rather than a nozzle. A linear actuator carries the needle down to a commanded insertion depth beside the target plant; a peristaltic pump then delivers a metered volume. The sequence is deliberately conservative in its timing: a 1500 ms pre-soak on the delivery channel before the actuator extends, a 4000 ms worst-case travel time backed by limit switches rather than by dead reckoning on the actuator, an 800 ms dwell at full insertion, and a 1500 ms injection pulse corresponding to approximately 1 ml at the peristaltic pump's rated 40 ml/min.

Injection rather than spraying is the more consequential choice. It eliminates the drift cloud that is the principal operator-exposure pathway and the principal off-target loss pathway. It also imposes a hard constraint on the rest of the machine, and it is the constraint that shapes the safety design: the vehicle must be stationary, and provably stationary, for the entire two-and-a-half-second dosing sequence with a needle below the soil surface. Section 6 describes how that is enforced.

## 5.3 Soil probe

A seven-parameter probe is read over Modbus RTU at 9600 baud, returning soil moisture, temperature, electrical conductivity, pH, and available nitrogen, phosphorus and potassium from seven consecutive holding registers. The transport is hardened against the electrical environment of a machine carrying two brushed motor drivers: a 1000 ms frame timeout, up to three retries on a failed read, and cyclic redundancy validation on every frame. A read that fails all retries is reported as a gap in the record and never as a zero, because a zero nutrient reading silently propagated into a prescription map is an error that ends in a wrong dose.

## 5.4 Power and thermal

The platform runs from a three-cell lithium-polymer pack, 12.6 V full and 11.1 V nominal, monitored through a 39 k / 10 k divider into the ESP32 analogue-to-digital converter with sixteen-fold oversampling and eFuse-calibrated reference. Crossing 9.9 V asserts a low-battery event that both inhibits drive and initiates return-to-base, so that the machine does not strand itself with a needle deployed. Die temperature is monitored with hysteresis, asserting an over-temperature event at 85 °C and clearing it only below 80 °C, which prevents the oscillation that a single-threshold design would produce at the margin.

# 6. Embedded Firmware and the Safety Architecture

## 6.1 Task structure

The FreeRTOS application is partitioned across both ESP32 cores by timing criticality. The drive task, which converts authenticated velocity commands into pulse-width outputs at 50 Hz, is pinned to core 1 together with the dosing sequencer. Sensor acquisition -- soil probe transactions, ultrasonic ranging, GNSS parsing, battery and temperature sampling -- runs on core 0, where a blocking Modbus timeout cannot delay a motor update. Each task carries a 4096-word stack and is registered with a task watchdog set to 5 s; a task that stops feeding the watchdog resets the controller, which de-energises the relay coils and brings the machine to a stop by construction rather than by recovery logic.

## 6.2 A single definition of "may not move"

The central design decision in the firmware is that the condition under which the machine may not move is defined exactly once. Nine event bits in a FreeRTOS event group represent the machine's safety-relevant state, and a single mask, EVT_DRIVE_INHIBIT, is the logical disjunction of the six that must stop motion. Table 2 lists the bits.

TABLE:
Event bit | Asserting condition | In drive-inhibit mask
EVT_HALT | Emergency stop asserted, tilt limit exceeded, or supervisory halt | Yes
EVT_LOW_BATTERY | Pack voltage below the 9.9 V cutoff; also triggers return-to-base | Yes
EVT_DOSING | Dosing sequence in progress; needle is or may be below soil | Yes
EVT_OBSTACLE | Ultrasonic range inside the 250 mm stop envelope | Yes
EVT_LINK_LOST | No valid signed command within the 1500 ms dead-man window | Yes
EVT_OVERTEMP | Controller die temperature at or above 85 °C | Yes
EVT_DOSE_REQUEST | Waypoint reached; dosing sequence requested | No
EVT_PAUSE_IRRIG | Rain detected, relayed from the perception tier | No
EVT_PUMP_DISABLE | Tank empty or supervisory override; blocks dosing only | No

Figure 2 shows how the mask is consumed. The drive task tests it before every pulse-width write, so the worst-case latency from any inhibiting condition to zero motor command is one 50 Hz control period. The dosing sequencer asserts EVT_DOSING for the whole sequence duration, which means the guarantee that the vehicle is stationary while the needle is down is not a matter of sequencing discipline in the dosing code but a property of the same mask the drive task already obeys.

FIG: fig2_safety_chain.png | The drive-inhibit chain. Six independent conditions map to six event bits; the bits are combined into one mask defined in a single header; every actuating task consumes that mask. The independent safety path shown at the base is electrical and is not represented in the event group at all, because it removes power from the controller rather than informing it.

The reason to insist on a single definition is that the common failure mode in machines of this class is not a missing interlock but a disagreeing one -- a dosing routine that believes motion is inhibited while the drive loop believes it is permitted. A shared mask makes that disagreement unrepresentable.

## 6.3 The path that software cannot reach

Above the event group sits a mechanism that the event group does not participate in. A latching mushroom-head emergency stop is wired to the ESP32 enable pin. Pressing it holds the controller in reset; the relay coils driving the pump and actuator are wired to de-energise in that state, which is also their state at power-on before firmware runs. No firmware path, no configuration value, and no supervisory command can override this, because by the time the state is entered the processor that would execute the override is not running.

We regard this as the single most important element of the design, and it is deliberately the least sophisticated. A safety argument that depends on software being correct is weaker than one that depends on a spring and a contact.

## 6.4 Supervisory fail-safe on sensor loss

Obstacle detection illustrates the general fault posture. Ranging uses a median of five ultrasonic pings to reject spurious echoes off crop foliage, with a 30 ms timeout. If the time-of-flight sensor becomes unavailable, the supervisory layer asserts a stop rather than continuing on the last known range. The machine's default in the absence of information is to stop, and there is no configuration in which that default is inverted.

# 7. Command Authentication

The command link is wireless, the operating environment is not access-controlled, and the payloads command a machine that carries chemical. Every motion and dosing command therefore carries an HMAC-SHA256 tag computed over the payload with a pre-shared key and truncated to 128 bits, which is adequate against forgery at this message rate while keeping the framing small enough for the serial path.

Replay is prevented by a monotonic counter that the receiver persists in non-volatile storage. A command whose counter does not exceed the last accepted value is discarded. Because flash endurance is finite and the counter advances at command rate, persistence is throttled to one write per 30 s, with the in-memory value authoritative between writes; the design accepts that a power loss may cost up to 30 s of counter advance, and treats that as strictly preferable to wearing out the storage that makes replay protection possible at all.

Eight consecutive signature failures place the receiver in a 10 s lockout during which no command is accepted, converting a brute-force or fuzzing attempt into a denial of motion rather than an opportunity. Because EVT_LINK_LOST is in the drive-inhibit mask, a lockout entered while the machine is moving stops the machine after the 1500 ms dead-man window elapses. The failure mode of the security layer is thus a stopped rover, which is the failure mode we want.

# 8. Perception, Navigation and Data Layers

## 8.1 Detection pipeline

Weed and disease detection use a quantised single-stage detector executed on board. The runtime is abstracted behind one interface with two implementations: a neural-accelerator backend and a CPU backend using a delegated 8-bit integer runtime. Backend selection is a configuration flag, and the pipeline above it is identical in both cases. As noted in Section 2.3, this is a supply-chain decision rather than a performance one -- it makes the build independent of whether a specific accelerator is obtainable.

Detections become physical targets through a calibrated camera-to-ground homography. A bounding box in image coordinates is projected to a ground offset relative to the rover, and that offset drives the dosing head. This projection is where perception accuracy becomes actuation accuracy, and it is validated in software against synthetic geometry in the test suite; its field validation is Gate 2.

## 8.2 State estimation

Localisation fuses three sources with complementary error characteristics: a GNSS receiver with satellite-based augmentation, which is unbiased but noisy at the metre scale; wheel odometry, which is smooth at short horizon but accumulates unbounded error through slip; and an inertial measurement unit supplying heading rate. An extended Kalman filter estimates the planar pose, propagating a unicycle model between updates and correcting on each fix.

The prediction step advances the state with the commanded body velocities:

MATH: x_{k|k-1} = x_{k-1} + v_k \Delta t \cos\theta_{k-1}, \qquad y_{k|k-1} = y_{k-1} + v_k \Delta t \sin\theta_{k-1}, \qquad \theta_{k|k-1} = \theta_{k-1} + \omega_k \Delta t

with covariance propagated as

MATH: P_{k|k-1} = F_k P_{k-1} F_k^{\top} + Q_k

where $F_k$ is the Jacobian of the motion model about the previous estimate and $Q_k$ is the process noise reflecting wheel slip and heading-rate error. A GNSS fix, converted to a local tangent frame, is applied as a linear position measurement:

MATH: K_k = P_{k|k-1} H^{\top} \left( H P_{k|k-1} H^{\top} + R_k \right)^{-1}, \qquad x_{k|k} = x_{k|k-1} + K_k \left( z_k - H x_{k|k-1} \right)

The engineering value of this arrangement is that neither source alone is sufficient. Odometry alone drifts without bound. GNSS alone is too noisy to hold a 0.60 m corridor: a 2.3 m error signal fed to a steering controller produces a machine that weaves across rows. The filter suppresses odometry drift with absolute fixes while suppressing fix noise with the motion model, and Section 8.5 quantifies the result.

## 8.3 Coverage planning and guidance

Field coverage uses a boustrophedon pattern generated from the plot polygon and the row spacing, with headland turns at each end. Guidance follows the resulting waypoint sequence with a pure-pursuit controller acting on the filtered pose. Figure 3 shows the plan for the simulated plot and the executed track at row scale.

FIG: fig3_coverage_path.png | Coverage geometry for a 20 m by 30 m plot at 0.60 m row spacing. Panel (a) is the full plan: 34 passes, 68 waypoints, 1039.8 m of path, equivalent to approximately 7013 m per acre. Panel (b) magnifies the first four passes to show the executed track against the planned row centre-line under EKF guidance.

The path length figure is the quantity that determines whether the concept is operationally viable at all. At 1039.8 m for 0.06 hectares, coverage scales to roughly 7 km of driving per acre, or approximately 50 min per plot of this size at the modelled traverse speed. This is the number that a battery specification and a mission-scheduling policy have to be built around, and it is why the mission scheduler supports resuming a partially completed plan rather than assuming a plot is covered in one charge.

## 8.4 Agronomic data layer

Soil probe readings are geo-referenced and accumulated into interpolated nutrient surfaces, from which prescription maps are generated. Maps export to ISO 11783-10 task data, which matters for a reason that is not technical: a smallholder's prescription becomes useful beyond the rover only if it can be read by the equipment and advisory software the rest of the value chain already uses, and a proprietary format forecloses that.

A per-plant database keys observations to position with a 0.5 m matching tolerance, so that the same plant observed on successive passes accumulates a history rather than generating duplicate records. Each dosing event is written to an append-only ledger with position, trigger, detection confidence, and the volume delivered, from which chemical volume avoided relative to a blanket application over the same swath is computed. We stress the interpretation of that computation: it is an arithmetic account of what the machine did and did not apply, given the swath and unit cost recorded in configuration. It is a measurement of machine behaviour, not an agronomic outcome, and it becomes a claim about chemical reduction only after Gate 5 establishes that the treated plants were the correct ones.

## 8.5 Simulation results

To isolate the contribution of state estimation to control performance, we ran a closed-loop simulation of the full guidance stack over the coverage plan of Figure 3. The rover is modelled as a unicycle with proportional wheel slip; GNSS is modelled with metre-scale noise at a low update rate; heading rate carries a bias. The same pure-pursuit controller and the same waypoint sequence are used in all conditions, so the only variable is the pose supplied to the controller. Table 3 reports the outcome.

TABLE:
Metric | Dead reckoning | Raw GNSS | EKF fusion
Position RMSE (m) | 17.893 | 2.256 | 0.943
Final position error (m) | 11.205 | -- | 1.169
Steady-state RMSE, after convergence (m) | -- | -- | 0.929
Cross-track error, RMS (m) | 13.817 | -- | 0.563
Cross-track error, maximum (m) | -- | -- | 2.276
Waypoints reached of 68 | 68 | -- | 68

Two readings of this table matter. The first is the position column: fusion improves on the better of its two inputs by a factor of 2.4, and on the worse by a factor of nineteen. The second, and the one with operational meaning, is the cross-track row: 0.563 m RMS under fusion against 13.817 m under dead reckoning. In a field with 0.60 m row spacing, the former is a machine that stays in its corridor and the latter is a machine that has left the field. The 2.276 m maximum cross-track excursion under fusion is not acceptable for row work and localises the remaining problem precisely -- it occurs at headland turns, where the pure-pursuit controller and the filter are both worst-conditioned, and it identifies turn handling rather than straight-line tracking as the next control work.

FIG: fig4_localisation_error.png | Position error against distance travelled for the three conditions of Table 3. Dead-reckoning error grows without bound as slip integrates; raw GNSS error is bounded but noisy at the metre scale; the fused estimate converges and remains sub-metre. The vertical scale is logarithmic.

These are simulation results under the stated models and they are reported as such. They establish that the navigation software is correct and that fusion is necessary; they do not establish field accuracy, which depends on real slip, real multipath and real canopy occlusion, and which is Gate 4.

## 8.6 Software verification

The Python tier carries 147 automated tests across ten modules, covering the navigation filter and planner, camera-to-ground geometry, the data pipeline and interpolation, ISO-XML export, frame capture, model over-the-air update and verification, health monitoring, the savings ledger, the alerting path, and detector post-processing. The full suite passes. The firmware carries unit tests for the event-mask logic, command authentication, replay rejection, and probe frame validation.

Table 4 states the verification status of each subsystem, distinguishing what is tested in software from what requires hardware.

TABLE:
Subsystem | Verified in software | Requires hardware validation
Navigation filter and planner | 147-test suite; closed-loop simulation | Field slip, multipath, canopy occlusion (Gate 4)
Detection pipeline | Synthetic geometry; post-processing tests | Accuracy on field imagery; frame rate on target (Gate 2)
Safety event mask | Firmware unit tests on mask logic | E-stop latency and relay state (Gate 1)
Command authentication | Signature and replay unit tests | Link behaviour under field interference
Soil probe interface | Frame parsing and retry logic | Reading repeatability in soil (Gate 3)
Dosing sequencer | Sequence timing and interlock tests | Volume accuracy; insertion reliability (Gate 3)
Data and export layer | Pipeline and ISO-XML tests | End-to-end record from a real pass (Gate 5)

# 9. Cost Analysis

Table 5 gives the planned bill of materials at Rs 41,150. The figure is a planning total against Indian retail pricing at the time of specification, exclusive of fabrication labour and of the spare-parts allowance that a field campaign requires.

TABLE:
Group | Principal items | Share of total
Compute | Raspberry Pi 5, ESP32 development board, storage | Largest single group
Drive | Two BTS7960 half-bridge modules, geared motors, wheel encoders | Second
Sensing | GNSS with augmentation, IMU, seven-parameter soil probe, ultrasonic ranging, camera | Second
Dosing | Linear actuator with limit switches, peristaltic pump, needle head, tank | Third
Power and safety | 3S lithium-polymer pack, regulation, latching E-stop, relays, wiring | Balance
Planned total | | Rs 41,150

The cost structure has a property worth naming: the safety-critical elements are among the cheapest. The latching emergency stop, the relays, and the voltage divider that detects a low pack together account for a small fraction of the total. There is no version of this machine in which safety was traded against cost, because at this scale safety is not what costs money.

# 10. Current Status, Validation Protocol and Limitations

## 10.1 Status

The software tiers are implemented and tested to the extent described in Section 8.6. The mechanical layout, wiring, and bill of materials are specified and documented. The physical rover has not been assembled. No bench integration, no tethered trial, and no field trial has been conducted, and consequently there is no measurement in this paper of detection accuracy on field imagery, dosing volume accuracy, chemical reduction, or any yield effect.

## 10.2 The six gates

Table 6 states the acceptance protocol. Each gate has an entry condition and a measured exit criterion, and no claim in the corresponding row may be made publicly until its gate is passed. The ordering is deliberate: safety is gated before autonomy, and autonomy before efficacy.

TABLE:
Gate | Stage | Exit criterion | Claim it licenses
1 | Bench interlock | E-stop holds controller in reset and relays de-energised in every state; all six inhibit conditions stop drive within one control period | The machine is safe to energise with chemical absent
2 | Bench perception | Detector frame rate and accuracy measured on held-out field imagery on target hardware | Detection performance may be quoted
3 | Bench dosing and probe | Dosing volume repeatability; probe reading repeatability across insertions at fixed depth | Dose and soil readings may be quoted
4 | Tethered plot | Row following inside the 0.60 m corridor over a full coverage plan with an operator on the E-stop | Autonomous navigation accuracy may be quoted
5 | Supervised plot, chemical | Complete pass with dosing; treated plants independently scored against ground truth | Targeting accuracy and chemical reduction may be quoted
6 | Multi-week field | Repeated passes across a season segment on a cooperating farm; durability, drift and record integrity | Agronomic and economic outcomes may be quoted

## 10.3 Limitations

Four limitations are structural rather than incidental. First, the simulation of Section 8.5 uses a proportional slip model and does not represent wheel sinkage in wet soil, which is the failure mode most likely to invalidate the odometry assumption; the 0.563 m cross-track figure should be expected to degrade in the field. Second, the 2.276 m maximum excursion at headland turns is a known control deficiency and not a noise artefact. Third, soil probe readings taken by a moving platform at actuator-set depth have unquantified repeatability, and Gate 3 exists because we do not know the answer. Fourth, the detector has not been evaluated on imagery from the crops and lighting conditions of a target smallholding, and detection performance on curated datasets is a poor predictor of performance under field dust, canopy shadow and the specific weed spectrum of a region.

A fifth limitation is economic rather than technical. A machine at Rs 41,150 in components is not a machine at Rs 41,150 to a farmer, and the path from this bill of materials to an affordable service -- shared ownership, custom-hiring, or a data-service model in which the audit trail is the product -- is outside the scope of this paper and unvalidated.

# 11. Conclusion

We have described AgriRover, a differential-drive agricultural robot designed to bring per-plant agrochemical decisions within reach of an Indian smallholding at a component cost of Rs 41,150. The engineering contributions are architectural. Separating hard real-time actuation on a FreeRTOS microcontroller from soft real-time perception on a single-board computer bounds the safety argument to a small, testable tier. Defining the drive-inhibit condition exactly once, as a mask in a single header consumed by every actuating task, makes interlock disagreement unrepresentable rather than merely unlikely. Wiring a latching mechanical stop to the controller enable pin places the final safety guarantee outside software entirely. Authenticating every motion command with a truncated HMAC and a persisted monotonic counter, and inhibiting drive on link loss, ensures that the failure mode of the security layer is a stopped machine.

We have quantified what is presently verifiable. A 147-test suite across ten modules passes, and a closed-loop simulation of a 34-pass coverage plan shows that fusing GNSS, odometry and inertial heading reduces localisation RMSE to 0.943 m from 2.256 m for GNSS alone and 17.893 m under dead reckoning, and reduces RMS cross-track error to 0.563 m from 13.817 m -- the difference between holding a 0.60 m row corridor and leaving the field. We have also been explicit that the rover is unbuilt, that no field data exists, and that every agronomic figure associated with this project is a target awaiting a gate.

The wider argument of the paper is about that last point. Agricultural robotics for smallholders is a field in which efficacy claims are cheap to make and expensive for the farmer who acts on them. Stating the acceptance protocol before the results, and separating what has been simulated from what has been measured, is not a caveat on the engineering; it is part of it.

# Acknowledgements

The authors thank the IDEAS programme at the Indian Institute of Technology Bombay for support, and the farming households in Jaunpur, Uttar Pradesh and Nashik, Maharashtra whose accounts of knapsack spraying shaped the requirements in Section 3.

# References

REF: Government of India, Ministry of Agriculture and Farmers Welfare. Agriculture Census: All India Report on Number and Area of Operational Holdings. New Delhi.
REF: Food and Agriculture Organization of the United Nations. Smallholders and Family Farms. FAO, Rome.
REF: Bechar, A. and Vigneault, C. Agricultural robots for field operations: concepts and components. Biosystems Engineering, vol. 149, pp. 94-111.
REF: Bechar, A. and Vigneault, C. Agricultural robots for field operations. Part 2: operations and systems. Biosystems Engineering, vol. 153, pp. 110-128.
REF: Oberti, R. et al. Selective spraying of grapevines for disease control using a modular agricultural robot. Biosystems Engineering, vol. 146, pp. 203-215.
REF: Slaughter, D. C., Giles, D. K. and Downey, D. Autonomous robotic weed control systems: a review. Computers and Electronics in Agriculture, vol. 61, no. 1, pp. 63-78.
REF: Thrun, S., Burgard, W. and Fox, D. Probabilistic Robotics. MIT Press, Cambridge, Massachusetts.
REF: Coulter, R. C. Implementation of the Pure Pursuit Path Tracking Algorithm. Technical Report CMU-RI-TR-92-01, Robotics Institute, Carnegie Mellon University.
REF: Choset, H. Coverage for robotics: a survey of recent results. Annals of Mathematics and Artificial Intelligence, vol. 31, pp. 113-126.
REF: International Organization for Standardization. ISO 11783-10: Tractors and machinery for agriculture and forestry -- Serial control and communications data network -- Part 10: Task controller and management information system data interchange. Geneva.
REF: International Electrotechnical Commission. IEC 61508: Functional safety of electrical/electronic/programmable electronic safety-related systems. Geneva.
REF: International Organization for Standardization. ISO 18497: Agricultural machinery and tractors -- Safety of highly automated agricultural machines. Geneva.
REF: Krishnaswamy, H. and Bahl, M. National Mission on Agricultural Extension and Technology: Sub-Mission on Agricultural Mechanization -- guidelines. Ministry of Agriculture and Farmers Welfare, New Delhi.
REF: Damalas, C. A. and Eleftherohorinos, I. G. Pesticide exposure, safety issues, and risk assessment indicators. International Journal of Environmental Research and Public Health, vol. 8, no. 5, pp. 1402-1419.
REF: Jocher, G. et al. Ultralytics YOLO. Open-source object detection framework documentation.
REF: David, R. et al. TensorFlow Lite Micro: embedded machine learning for TinyML systems. Proceedings of Machine Learning and Systems, vol. 3, pp. 800-811.
REF: Modbus Organization. MODBUS over Serial Line Specification and Implementation Guide, version 1.02.
REF: Krajnik, T. et al. A practical multirobot localization system. Journal of Intelligent and Robotic Systems, vol. 76, pp. 539-562.
