import xml.sax


class EventHandler(xml.sax.ContentHandler):
    def __init__(self, target):
        self.target = target

    def startElement(self, name, attrs):
        self.target(("start", (name, attrs._attrs)))

    def characters(self, text):
        self.target(("text", text))

    def endElement(self, name):
        self.target(("end", name))


def buses_to_dicts(target):
    busdict = {}
    fragments = []

    def business_logic(inpt):
        nonlocal busdict
        nonlocal fragments
        event, value = inpt
        if event == "start":
            fragments = []
            if value[0] == "bus":
                busdict = {}
        elif event == "text":
            fragments.append(value)
        elif event == "end":
            if value != "bus":
                busdict[value] = "".join(fragments)
            else:
                target(busdict)

    return business_logic


def filter_on_field(fieldname, value, target):
    def business_logic(d):
        if d.get(fieldname) == value:
            target(d)

    return business_logic


def bus_locations(bus):
    print(
        f"""{bus['route']}s,{bus['id']}s,{bus['direction']}s,
{bus['latitude']}s,{bus['longitude']}s"""
    )


if __name__ == "__main__":
    import sys

    args = sys.argv
    if len(args) < 2:
        print(f"Usage: {args[0]} xml_file_to_parse")
        sys.exit()

    xml.sax.parse(
        args[1],
        EventHandler(
            buses_to_dicts(
                filter_on_field(
                    "route",
                    "22",
                    filter_on_field("direction", "North Bound", bus_locations),
                )
            )
        ),
    )
