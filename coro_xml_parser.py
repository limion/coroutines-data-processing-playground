import xml.sax


class EventHandler(xml.sax.ContentHandler):
    def __init__(self, target):
        self.target = target

    def startElement(self, name, attrs):
        self.target.send(("start", (name, attrs._attrs)))

    def characters(self, text):
        self.target.send(("text", text))

    def endElement(self, name):
        self.target.send(("end", name))


def coroutine(f):
    def wrap(*args, **kwargs):
        cr = f(*args, **kwargs)
        next(cr)
        return cr

    return wrap


@coroutine
def buses_to_dicts(target):
    while True:
        event, value = yield
        # Look for the start of a <bus> element
        if event == "start" and value[0] == "bus":
            busdict = {}
            fragments = []
            # Capture text of inner elements in a dict
            while True:
                event, value = yield
                if event == "start":
                    fragments = []
                elif event == "text":
                    fragments.append(value)
                elif event == "end":
                    if value != "bus":
                        busdict[value] = "".join(fragments)
                    else:
                        target.send(busdict)
                        break


@coroutine
def filter_on_field(fieldname, value, target):
    while True:
        d = yield
        if d.get(fieldname) == value:
            target.send(d)


@coroutine
def bus_locations():
    while True:
        bus = yield
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
                    filter_on_field("direction", "North Bound", bus_locations()),
                )
            )
        ),
    )
