from paraview.simple import *
import os

# Disable auto camera reset
paraview.simple._DisableFirstRenderCameraReset()

# Create render view
renderView = GetActiveViewOrCreate('RenderView')
renderView.ViewSize = [1920, 1080]

# Load OpenFOAM case
reader = OpenFOAMReader(FileName="case.foam")
reader.MeshRegions = ['internalMesh']
reader.CellArrays = ['U', 'T', 'p', 'p_rgh', 'rho']
reader.UpdatePipeline()

timesteps = reader.TimestepValues
print("Available timesteps:", timesteps)

# Case bounds for slice location
bounds = reader.GetDataInformation().GetBounds()
xmid = 0.5 * (bounds[0] + bounds[1])
ymid = 0.5 * (bounds[2] + bounds[3])
zmid = 0.1 * (bounds[4] + bounds[5])
print("bounds", bounds)

# Output folder
outdir = "screenshots_3"
os.makedirs(outdir, exist_ok=True)

# Loop over timesteps
for t in timesteps:
    print(f"⏳ Processing timestep {t} ...")
    reader.UpdatePipeline(time=t)

    # ---- U Slice ----
    sliceU = Slice(Input=reader)
    sliceU.SliceType = 'Plane'
    sliceU.SliceType.Origin = [xmid, ymid, zmid]
    sliceU.SliceType.Normal = [1, 0, 0]

    calcU = Calculator(Input=sliceU)
    calcU.ResultArrayName = "U_mag"
    calcU.Function = "mag(U)"

    dispU = Show(calcU, renderView)
    ColorBy(dispU, ('POINTS', 'U_mag'))
    dispU.RescaleTransferFunctionToDataRange(True)

    renderView.ResetCamera()
    renderView.Update()
    
    SaveScreenshot(os.path.join(outdir, f"U_slice_t_{int(t)}.png"), renderView, ImageResolution=[1920, 1080])

    # Clean up the U slice pipeline objects
    Delete(dispU)
    Delete(calcU)
    Delete(sliceU)

    # ---- T Slice ----
    sliceT = Slice(Input=reader)
    sliceT.SliceType = 'Plane'
    sliceT.SliceType.Origin = [xmid, ymid, zmid]
    sliceT.SliceType.Normal = [1, 0, 0]

    calcT = Calculator(Input=sliceT)
    calcT.ResultArrayName = "T_copy"
    calcT.Function = "T"

    dispT = Show(calcT, renderView)
    ColorBy(dispT, ('POINTS', 'T_copy'))
    dispT.RescaleTransferFunctionToDataRange(True)
    
    # Explicitly set the camera position for the new slice
    # This is often more reliable than ResetCamera() for angled slices
    renderView.CameraPosition = [2, 0 , 0 ] 
    renderView.CameraFocalPoint = [xmid, ymid, zmid]
    renderView.CameraViewUp = [0, 2, 0] # Adjust view up for better perspective
    print(renderView.CameraPosition)
    
    # A final reset to ensure the slice is in view after manual adjustments
    renderView.ResetCamera()
    renderView.Update()
    
    SaveScreenshot(os.path.join(outdir, f"T_slice_t_{int(t)}.png"), renderView, ImageResolution=[1920, 1080])

    # Clean up the T slice pipeline objects
    Delete(dispT)
    Delete(calcT)
    Delete(sliceT)

    print(f"✅ Saved U_slice_t_{int(t)}.png and T_slice_t_{int(t)}.png")

print("🎉 All timesteps processed! Images are in 'screenshots_new/' folder.")