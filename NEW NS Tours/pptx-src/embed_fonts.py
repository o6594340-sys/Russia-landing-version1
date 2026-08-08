import sys, os
import win32com.client

src = os.path.abspath(sys.argv[1])
dst = os.path.abspath(sys.argv[2])

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
powerpoint.Visible = 1
pres = powerpoint.Presentations.Open(src, WithWindow=False)
try:
    pres.SaveAs(dst, 24, True)  # 24 = ppSaveAsOpenXMLPresentation (.pptx), EmbedTrueTypeFonts=True
    print("saved with embedded fonts:", dst)
except Exception as e:
    print("EmbedTrueTypeFonts SaveAs failed:", e)
    pres.SaveAs(dst, 24)
    print("saved WITHOUT embedded fonts:", dst)
finally:
    pres.Close()
    powerpoint.Quit()
