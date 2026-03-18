from database import SessionLocal, engine
import models


def seed_db():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if already seeded
    existing = db.query(models.Problem).first()
    if existing:
        print("Database already seeded. Delete extrusion_ai.db to re-seed.")
        db.close()
        return

    print("Seeding initial data...")

    # ═══════════════════════════════════════════════════════════════
    #  Machines
    # ═══════════════════════════════════════════════════════════════
    machines = [
        models.Machine(name="Single Screw Extruder 90mm", machine_type="extrusion",
                        manufacturer="KraussMaffei", model_number="KME 90"),
        models.Machine(name="Twin Screw Extruder 60mm", machine_type="extrusion",
                        manufacturer="Coperion", model_number="ZSK 60"),
        models.Machine(name="Injection Molding 250T", machine_type="injection",
                        manufacturer="Engel", model_number="Victory 250"),
        models.Machine(name="Injection Molding 500T", machine_type="injection",
                        manufacturer="Arburg", model_number="Allrounder 520A"),
        models.Machine(name="Blow Molding Machine B10", machine_type="blow_molding",
                        manufacturer="Bekum", model_number="BM-10"),
        models.Machine(name="Blow Molding Machine B30", machine_type="blow_molding",
                        manufacturer="Kautex", model_number="KBS 30"),
    ]
    db.add_all(machines)

    # ═══════════════════════════════════════════════════════════════
    #  Materials
    # ═══════════════════════════════════════════════════════════════
    materials = [
        models.Material(name="High Density Polyethylene", material_type="HDPE",
                         melt_temp_min=180, melt_temp_max=230,
                         recommended_screw_speed_min=20, recommended_screw_speed_max=80,
                         max_regrind_percentage=25),
        models.Material(name="Low Density Polyethylene", material_type="LDPE",
                         melt_temp_min=160, melt_temp_max=220,
                         recommended_screw_speed_min=20, recommended_screw_speed_max=70,
                         max_regrind_percentage=30),
        models.Material(name="Polypropylene", material_type="PP",
                         melt_temp_min=200, melt_temp_max=280,
                         recommended_screw_speed_min=30, recommended_screw_speed_max=100,
                         max_regrind_percentage=20),
        models.Material(name="Polyvinyl Chloride", material_type="PVC",
                         melt_temp_min=150, melt_temp_max=200,
                         recommended_screw_speed_min=15, recommended_screw_speed_max=50,
                         max_regrind_percentage=10),
        models.Material(name="Polystyrene", material_type="PS",
                         melt_temp_min=180, melt_temp_max=260,
                         recommended_screw_speed_min=25, recommended_screw_speed_max=80,
                         max_regrind_percentage=20),
        models.Material(name="Acrylonitrile Butadiene Styrene", material_type="ABS",
                         melt_temp_min=210, melt_temp_max=270,
                         recommended_screw_speed_min=30, recommended_screw_speed_max=70,
                         max_regrind_percentage=15),
        models.Material(name="Polyethylene Terephthalate", material_type="PET",
                         melt_temp_min=260, melt_temp_max=290,
                         recommended_screw_speed_min=20, recommended_screw_speed_max=60,
                         max_regrind_percentage=10),
        models.Material(name="Polyamide (Nylon)", material_type="PA",
                         melt_temp_min=230, melt_temp_max=290,
                         recommended_screw_speed_min=25, recommended_screw_speed_max=80,
                         max_regrind_percentage=15),
        models.Material(name="Polycarbonate", material_type="PC",
                         melt_temp_min=260, melt_temp_max=320,
                         recommended_screw_speed_min=20, recommended_screw_speed_max=60,
                         max_regrind_percentage=10),
    ]
    db.add_all(materials)

    # ═══════════════════════════════════════════════════════════════
    #  Problems & Solutions — EXTRUSION
    # ═══════════════════════════════════════════════════════════════

    # 1. Uneven Wall Thickness
    p1 = models.Problem(
        problem_name="Uneven Wall Thickness",
        process_type="extrusion",
        description="The wall thickness of the extruded profile or pipe is not uniform around its circumference.",
        severity="high",
        defect_category="uneven_wall_thickness",
        machine_parameters={"melt_temperature": "high", "die_temperature": "uneven", "screw_speed": "variable"}
    )
    db.add(p1)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p1.id, step_order=1, description="Check die mandrel centering",
                         details="Use dial indicator to measure mandrel position. Max deviation: 0.05mm."),
        models.Solution(problem_id=p1.id, step_order=2, description="Adjust extrusion rate",
                         details="Reduce screw speed by 5-10% and monitor wall thickness distribution."),
        models.Solution(problem_id=p1.id, step_order=3, description="Check mold alignment",
                         details="Verify mold halves are aligned using alignment pins. Re-torque bolts evenly."),
        models.Solution(problem_id=p1.id, step_order=4, description="Adjust parison program",
                         details="Modify parison programming to compensate for uneven stretching."),
    ])

    # 2. Melt Fracture
    p2 = models.Problem(
        problem_name="Melt Fracture",
        process_type="extrusion",
        description="Surface roughness or sharkskin appearance on the extrudate caused by excessive shear stress at the die exit.",
        severity="high",
        defect_category="melt_fracture",
        machine_parameters={"melt_temperature": "low", "extrusion_pressure": "high", "screw_speed": "high"}
    )
    db.add(p2)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p2.id, step_order=1, description="Increase die temperature",
                         details="Raise die temperature by 10-20°C to reduce melt viscosity at the die exit."),
        models.Solution(problem_id=p2.id, step_order=2, description="Decrease extrusion speed",
                         details="Reduce screw speed by 15-25% to lower shear rate."),
        models.Solution(problem_id=p2.id, step_order=3, description="Increase die land length",
                         details="Use a die with longer land to allow stress relaxation before exit."),
        models.Solution(problem_id=p2.id, step_order=4, description="Apply processing aid",
                         details="Add fluoropolymer processing aid at 0.02-0.05% concentration."),
    ])

    # 3. Burn Marks (Extrusion)
    p3 = models.Problem(
        problem_name="Burn Marks on Extrudate",
        process_type="extrusion",
        description="Dark brown or black discoloration on the extruded product surface caused by thermal degradation.",
        severity="critical",
        defect_category="burn_marks",
        machine_parameters={"melt_temperature": "very_high", "screw_speed": "high", "die_temperature": "high"}
    )
    db.add(p3)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p3.id, step_order=1, description="Reduce melt temperature",
                         details="Lower barrel temperature by 10-15°C in the metering zone."),
        models.Solution(problem_id=p3.id, step_order=2, description="Reduce screw speed",
                         details="Lower RPM to decrease shear heating. Check for dead spots."),
        models.Solution(problem_id=p3.id, step_order=3, description="Clean barrel and screw",
                         details="Purge with cleaning compound. Disassemble and manually clean if necessary."),
        models.Solution(problem_id=p3.id, step_order=4, description="Check for material degradation",
                         details="Verify material moisture content and storage conditions. Check regrind quality."),
    ])

    # 4. Bubbles (Extrusion)
    p4 = models.Problem(
        problem_name="Bubbles in Extrudate",
        process_type="extrusion",
        description="Air or gas pockets trapped within the extruded product, causing voids and surface defects.",
        severity="medium",
        defect_category="bubbles",
        machine_parameters={"melt_temperature": "high", "screw_speed": "high", "extrusion_pressure": "low"}
    )
    db.add(p4)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p4.id, step_order=1, description="Check material drying",
                         details="Verify material is dried to manufacturer spec. Increase drying time if needed."),
        models.Solution(problem_id=p4.id, step_order=2, description="Increase back pressure",
                         details="Raise back pressure to improve melt homogeneity and gas expulsion."),
        models.Solution(problem_id=p4.id, step_order=3, description="Reduce screw speed",
                         details="Lower RPM to reduce air entrainment in the feed section."),
        models.Solution(problem_id=p4.id, step_order=4, description="Check vacuum venting",
                         details="Ensure venting ports are clear and vacuum system is functioning properly."),
    ])

    # 5. Streaks (Extrusion)
    p5 = models.Problem(
        problem_name="Streaks on Surface",
        process_type="extrusion",
        description="Visible lines or streaks on the extrudate surface, often caused by contamination or damage.",
        severity="medium",
        defect_category="streaks",
        machine_parameters={"die_temperature": "uneven", "screw_speed": "normal"}
    )
    db.add(p5)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p5.id, step_order=1, description="Inspect and clean the die",
                         details="Remove die and inspect for scratches, buildup, or damage on land surfaces."),
        models.Solution(problem_id=p5.id, step_order=2, description="Check material contamination",
                         details="Inspect raw material for foreign particles. Check regrind for contamination."),
        models.Solution(problem_id=p5.id, step_order=3, description="Verify color masterbatch dispersion",
                         details="Ensure proper mixing ratio and dispersion of colorant or additives."),
    ])

    # ═══════════════════════════════════════════════════════════════
    #  Problems & Solutions — INJECTION MOLDING
    # ═══════════════════════════════════════════════════════════════

    # 6. Flash (Injection)
    p6 = models.Problem(
        problem_name="Flash on Molded Part",
        process_type="injection",
        description="Excess material escaping from the mold parting line, creating thin fins or excess material on the part edges.",
        severity="medium",
        defect_category="flash",
        machine_parameters={"melt_temperature": "high", "extrusion_pressure": "high", "mold_temperature": "high"}
    )
    db.add(p6)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p6.id, step_order=1, description="Reduce injection pressure",
                         details="Lower injection pressure by 5-15%. Check if fill is still complete."),
        models.Solution(problem_id=p6.id, step_order=2, description="Reduce packing pressure",
                         details="Lower packing/hold pressure and shorten packing time."),
        models.Solution(problem_id=p6.id, step_order=3, description="Increase clamp tonnage",
                         details="Ensure clamp force exceeds cavity pressure. May need larger machine."),
        models.Solution(problem_id=p6.id, step_order=4, description="Inspect mold parting surfaces",
                         details="Check for wear, damage, or contamination on the parting line surfaces."),
        models.Solution(problem_id=p6.id, step_order=5, description="Reduce melt temperature",
                         details="Lower barrel temperatures to increase melt viscosity."),
    ])

    # 7. Warpage (Injection)
    p7 = models.Problem(
        problem_name="Part Warpage",
        process_type="injection",
        description="Part deformation after ejection due to uneven cooling, stress, or improper gate location.",
        severity="high",
        defect_category="warpage",
        machine_parameters={"mold_temperature": "uneven", "cooling_time": "short", "melt_temperature": "high"}
    )
    db.add(p7)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p7.id, step_order=1, description="Increase cooling time",
                         details="Extend cooling time by 20-30% to allow uniform part solidification."),
        models.Solution(problem_id=p7.id, step_order=2, description="Balance mold temperature",
                         details="Ensure both mold halves are at the same temperature. Check coolant flow."),
        models.Solution(problem_id=p7.id, step_order=3, description="Reduce melt temperature",
                         details="Lower barrel temperature to reduce residual stress in the molded part."),
        models.Solution(problem_id=p7.id, step_order=4, description="Adjust gate location",
                         details="Consider relocating or adding gates for more uniform fill pattern."),
    ])

    # 8. Burn Marks (Injection)
    p8 = models.Problem(
        problem_name="Burn Marks on Injected Part",
        process_type="injection",
        description="Dark discoloration at the end of fill, caused by trapped air compression or material degradation.",
        severity="critical",
        defect_category="burn_marks",
        machine_parameters={"melt_temperature": "high", "cycle_time": "long", "extrusion_pressure": "high"}
    )
    db.add(p8)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p8.id, step_order=1, description="Reduce injection speed",
                         details="Slow down injection speed at end of fill to allow air to escape."),
        models.Solution(problem_id=p8.id, step_order=2, description="Improve mold venting",
                         details="Add or deepen vents at the last-to-fill areas. Vent depth: 0.02-0.05mm."),
        models.Solution(problem_id=p8.id, step_order=3, description="Reduce melt temperature",
                         details="Lower barrel temperatures to prevent thermal degradation."),
        models.Solution(problem_id=p8.id, step_order=4, description="Reduce clamp force",
                         details="Excessive clamp can close vents. Reduce to minimum needed."),
    ])

    # 9. Bubbles / Voids (Injection)
    p9 = models.Problem(
        problem_name="Bubbles and Voids in Molded Part",
        process_type="injection",
        description="Internal voids or surface bubbles caused by insufficient packing, moisture, or trapped gas.",
        severity="high",
        defect_category="bubbles",
        machine_parameters={"melt_temperature": "high", "cooling_time": "short", "extrusion_pressure": "low"}
    )
    db.add(p9)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p9.id, step_order=1, description="Increase packing pressure and time",
                         details="Higher packing compensates for material shrinkage during solidification."),
        models.Solution(problem_id=p9.id, step_order=2, description="Dry the material thoroughly",
                         details="Check moisture content with analyzer. Dry per material manufacturer specs."),
        models.Solution(problem_id=p9.id, step_order=3, description="Reduce melt temperature",
                         details="Lower barrel temperature to reduce gas generation from degradation."),
        models.Solution(problem_id=p9.id, step_order=4, description="Increase gate size",
                         details="Larger gate allows packing pressure to reach thick sections."),
    ])

    # 10. Streaks (Injection)
    p10 = models.Problem(
        problem_name="Color Streaks in Molded Part",
        process_type="injection",
        description="Inconsistent color distribution creating visible streaks or marbling in the part.",
        severity="medium",
        defect_category="streaks",
        machine_parameters={"melt_temperature": "low", "screw_speed": "low"}
    )
    db.add(p10)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p10.id, step_order=1, description="Increase screw speed and back pressure",
                         details="Higher mixing action improves color homogeneity."),
        models.Solution(problem_id=p10.id, step_order=2, description="Increase melt temperature",
                         details="Higher temperature improves material flow and mixing."),
        models.Solution(problem_id=p10.id, step_order=3, description="Check masterbatch dosing",
                         details="Verify dosing percentage and consistency of color feeder."),
    ])

    # ═══════════════════════════════════════════════════════════════
    #  Problems & Solutions — BLOW MOLDING
    # ═══════════════════════════════════════════════════════════════

    # 11. Uneven Wall Thickness (Blow Molding)
    p11 = models.Problem(
        problem_name="Uneven Wall Thickness in Blow Molded Part",
        process_type="blow_molding",
        description="Non-uniform wall distribution in blow molded containers, causing weak spots.",
        severity="high",
        defect_category="uneven_wall_thickness",
        machine_parameters={"melt_temperature": "high", "die_temperature": "uneven", "extrusion_pressure": "variable"}
    )
    db.add(p11)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p11.id, step_order=1, description="Adjust parison programming",
                         details="Modify wall thickness profile to compensate for stretching variations."),
        models.Solution(problem_id=p11.id, step_order=2, description="Center the die tooling",
                         details="Use adjusting bolts to center mandrel. Verify with parison measurement."),
        models.Solution(problem_id=p11.id, step_order=3, description="Optimize blow pressure",
                         details="Adjust pre-blow and final blow pressures for uniform material distribution."),
        models.Solution(problem_id=p11.id, step_order=4, description="Check mold clamping",
                         details="Verify mold halves close uniformly. Check for worn tie bars or platens."),
    ])

    # 12. Flash (Blow Molding)
    p12 = models.Problem(
        problem_name="Flash on Blow Molded Part",
        process_type="blow_molding",
        description="Excess material squeezed out at the pinch-off area, causing visible flash or weak seams.",
        severity="medium",
        defect_category="flash",
        machine_parameters={"melt_temperature": "high", "extrusion_pressure": "high"}
    )
    db.add(p12)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p12.id, step_order=1, description="Reduce parison weight",
                         details="Decrease wall thickness to reduce material at pinch-off."),
        models.Solution(problem_id=p12.id, step_order=2, description="Check pinch-off geometry",
                         details="Inspect pinch-off area for wear. Re-machine if clearance is excessive."),
        models.Solution(problem_id=p12.id, step_order=3, description="Increase clamp force",
                         details="Ensure sufficient tonnage to seal parison. Check hydraulic pressure."),
        models.Solution(problem_id=p12.id, step_order=4, description="Reduce melt temperature",
                         details="Lower temperature makes the parison stiffer, reducing squeeze-out."),
    ])

    # 13. Bubbles (Blow Molding)
    p13 = models.Problem(
        problem_name="Bubbles in Blow Molded Container",
        process_type="blow_molding",
        description="Air or gas bubbles trapped in the wall of blow molded containers.",
        severity="medium",
        defect_category="bubbles",
        machine_parameters={"melt_temperature": "high", "screw_speed": "high"}
    )
    db.add(p13)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p13.id, step_order=1, description="Dry material properly",
                         details="Moisture is the primary cause. Dry to <0.02% moisture content."),
        models.Solution(problem_id=p13.id, step_order=2, description="Reduce melt temperature",
                         details="Lower barrel temperatures to prevent material degradation and gas formation."),
        models.Solution(problem_id=p13.id, step_order=3, description="Reduce regrind percentage",
                         details="Limit regrind to manufacturer-recommended levels. Check regrind quality."),
    ])

    # 14. Warpage (Blow Molding)
    p14 = models.Problem(
        problem_name="Warpage in Blow Molded Part",
        process_type="blow_molding",
        description="Part distortion after ejection due to uneven cooling, premature ejection, or residual stress.",
        severity="high",
        defect_category="warpage",
        machine_parameters={"mold_temperature": "uneven", "cooling_time": "short", "melt_temperature": "high"}
    )
    db.add(p14)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p14.id, step_order=1, description="Increase cooling time",
                         details="Part must be rigid enough before ejection. Extend cooling by 15-25%."),
        models.Solution(problem_id=p14.id, step_order=2, description="Balance mold cooling",
                         details="Check coolant flow rates and temperatures on both mold halves."),
        models.Solution(problem_id=p14.id, step_order=3, description="Reduce mold temperature differential",
                         details="Minimize temperature difference between core and cavity sides."),
        models.Solution(problem_id=p14.id, step_order=4, description="Adjust blow air timing",
                         details="Use internal cooling air to speed up uniform part cooling."),
    ])

    # 15. Melt Fracture (Blow Molding)
    p15 = models.Problem(
        problem_name="Melt Fracture on Blow Molded Part",
        process_type="blow_molding",
        description="Rough, shark-skin surface on the parison, carried through to the final part surface.",
        severity="high",
        defect_category="melt_fracture",
        machine_parameters={"melt_temperature": "low", "extrusion_pressure": "high", "screw_speed": "high"}
    )
    db.add(p15)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p15.id, step_order=1, description="Increase die temperature",
                         details="Raise die zone temperature by 10-20°C to reduce surface shear stress."),
        models.Solution(problem_id=p15.id, step_order=2, description="Reduce extrusion rate",
                         details="Lower screw RPM to decrease shear rate at the die exit."),
        models.Solution(problem_id=p15.id, step_order=3, description="Use processing aid",
                         details="Add 0.02-0.05% fluoropolymer processing aid to the material."),
        models.Solution(problem_id=p15.id, step_order=4, description="Polish die land surface",
                         details="Mirror-polish the die land area to reduce surface friction."),
    ])

    # 16. Burn Marks (Blow Molding)
    p16 = models.Problem(
        problem_name="Burn Marks on Blow Molded Part",
        process_type="blow_molding",
        description="Dark spots or streaks on the part surface from thermal degradation of the polymer.",
        severity="critical",
        defect_category="burn_marks",
        machine_parameters={"melt_temperature": "very_high", "cycle_time": "long", "screw_speed": "high"}
    )
    db.add(p16)
    db.flush()
    db.add_all([
        models.Solution(problem_id=p16.id, step_order=1, description="Reduce barrel temperature",
                         details="Lower temperature profile, especially in the metering and die adapter zones."),
        models.Solution(problem_id=p16.id, step_order=2, description="Reduce residence time",
                         details="Speed up cycle or reduce shot capacity to minimize heat exposure."),
        models.Solution(problem_id=p16.id, step_order=3, description="Purge and clean the extruder",
                         details="Run purging compound to remove degraded material from dead spots."),
    ])

    db.commit()
    db.close()
    print(f"Seed complete! Added {len(machines)} machines, {len(materials)} materials, 16 problems with solutions.")


if __name__ == "__main__":
    seed_db()
