import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        rootComp = design.rootComponent

        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        outerRadius = 12.0
        innerRadius = 10.0
        circles.addByCenterRadius(center, outerRadius)

        prof = sketch.profiles.item(0)

        extrudes = rootComp.features.extrudeFeatures
        distance = adsk.core.ValueInput.createByReal(20.0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput.setDistanceExtent(False, distance)
        ext = extrudes.add(extInput)

        body = ext.bodies.item(0)

        shellFeats = rootComp.features.shellFeatures
        faces = adsk.core.ObjectCollection.create()
        # shell from the top face to hollow the cylinder
        topFace = None
        for f in body.faces:
            if abs(f.boundingBox.maxPoint.z - body.boundingBox.maxPoint.z) < 1e-6:
                topFace = f
                break
        if topFace:
            faces.add(topFace)
            thickness = adsk.core.ValueInput.createByReal(2.0)
            shellInput = shellFeats.createInput(faces, True)
            shellInput.insideThickness = thickness
            shellFeats.add(shellInput)

        # Add a fillet to the top edge
        filletFeats = rootComp.features.filletFeatures
        edgeCollection = adsk.core.ObjectCollection.create()
        for e in body.edges:
            if abs(e.boundingBox.maxPoint.z - body.boundingBox.maxPoint.z) < 1e-6:
                edgeCollection.add(e)
        if edgeCollection.count > 0:
            filletInput = filletFeats.createInput()
            filletInput.addConstantRadiusEdgeSet(edgeCollection, adsk.core.ValueInput.createByReal(1.5), True)
            filletFeats.add(filletInput)

        ui.messageBox('Ice-cream holder created successfully')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

