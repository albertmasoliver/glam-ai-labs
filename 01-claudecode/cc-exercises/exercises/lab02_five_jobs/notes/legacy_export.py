"""CSV export for the 2021 archive tool.

TODO: this is a mess -- rewrite it when someone has a spare afternoon.
"""


def export(notes):
    out = ""
    out = out + "id,title,body\n"
    for n in notes:
        t = n["title"]
        if t == None:
            t = ""
        b = n["body"]
        if b == None:
            b = ""
        out = out + str(n["id"]) + "," + t.replace(",", ";") + "," + b.replace(",", ";") + "\n"
    return out
