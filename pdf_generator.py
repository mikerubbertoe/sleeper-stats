import magic
from reportlab.pdfgen import canvas
import reportlab.lib.pagesizes as ps
import re

def hello(c):
    #c.drawString(100,100,"Hello World")
    #c.drawInlineImage("reports/week/week_1_report.png", 20, 700, 790, 500)
    c.drawInlineImage("reports/week/week_2_report.png", 0, 0, 1389 *.60, 848 *.60)

c = canvas.Canvas("hello.pdf", ps.A3)
t = magic.from_file('reports/week/week_1_report.png')
x = re.search('(\d+) x (\d+)', t).groups()
print(x)
length, width = ps.A3
print(length, width)
hello(c)
c.showPage()
c.save()