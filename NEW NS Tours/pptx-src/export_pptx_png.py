import sys, os
import win32com.client

pptx_path = os.path.abspath(sys.argv[1])
out_dir = os.path.abspath(sys.argv[2])
os.makedirs(out_dir, exist_ok=True)

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
powerpoint.Visible = 1
pres = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
pres.SaveAs(os.path.join(out_dir, "slide"), 18)  # 18 = ppSaveAsPNG (exports all slides)
pres.Close()
powerpoint.Quit()
print("done")
