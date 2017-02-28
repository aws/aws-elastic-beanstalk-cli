import json
import os
import codecs
import sys

ESC_CHAR = 27
ERASE_LINE_CTRL_CODE = '[2K'
CURSOR_UP_CTRL_CODE = '[%dA'
CURSOR_DOWN_CTRL_CODE = '[%dB'

class StreamOutputError(Exception):
    pass


def stream_output(output, stream):
    is_terminal = hasattr(stream, 'fileno') and os.isatty(stream.fileno())
    if sys.version_info[0] < 3:
        stream = codecs.getwriter('utf-8')(stream)
    all_events = []
    lines = {}
    diff = 0

    print(output)
    for chunk in output:
        print(chunk)
        event = json.loads(chunk)
        all_events.append(event)

        if 'progress' in event or 'progressDetail' in event:
            image_id = event.get('id')
            if not image_id:
                continue

            if image_id in lines:
                diff = len(lines) - lines[image_id]
            else:
                lines[image_id] = len(lines)
                stream.write("\n")
                diff = 0

            if is_terminal:
                # move cursor up `diff` rows
                stream.write("%c%s" % (ESC_CHAR, (CURSOR_UP_CTRL_CODE % diff)))

        print_output_event(event, stream, is_terminal)

        if 'id' in event and is_terminal:
            # move cursor back down
            stream.write("%c%s" % (ESC_CHAR, (CURSOR_DOWN_CTRL_CODE % diff)))

        stream.flush()

    return all_events


def print_output_event(event, stream, is_terminal):
    if 'errorDetail' in event:
        raise StreamOutputError(event['errorDetail']['message'])

    terminator = ''

    if is_terminal and 'stream' not in event:
        # erase current line
        stream.write("%c%s\r" % (ESC_CHAR, ERASE_LINE_CTRL_CODE))
        terminator = "\r"
        pass
    elif 'progressDetail' in event:
        return

    if 'time' in event:
        stream.write("[%s] " % event['time'])

    if 'id' in event:
        stream.write("%s: " % event['id'])

    if 'from' in event:
        stream.write("(from %s) " % event['from'])

    status = event.get('status', '')

    if 'progress' in event:
        stream.write("%s %s%s" % (status, event['progress'], terminator))
    elif 'progressDetail' in event:
        detail = event['progressDetail']
        if 'current' in detail:
            percentage = float(detail['current']) / float(detail['total']) * 100
            stream.write('%s (%.1f%%)%s' % (status, percentage, terminator))
        else:
            stream.write('%s%s' % (status, terminator))
    elif 'stream' in event:
        stream.write("%s%s" % (event['stream'], terminator))
    else:
        stream.write("%s%s\n" % (status, terminator))
