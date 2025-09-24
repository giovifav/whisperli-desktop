import pathlib
import re
import xml.etree.ElementTree as ET

def fix_ts_file(path: pathlib.Path):
    print(f"🔧 Controllo: {path}")
    tree = ET.parse(path)
    root = tree.getroot()
    changed = False

    # Itera su tutti i messaggi
    for message in root.findall(".//message"):
        # 1️⃣ Rimuove type="finished"
        if 'type' in message.attrib and message.attrib['type'] == 'finished':
            del message.attrib['type']
            changed = True

        # 2️⃣ Escapa & non validi
        for elem in message.iter():
            if elem.text:
                new_text = re.sub(r'&(?!lt;|gt;|amp;)', '&amp;', elem.text)
                if new_text != elem.text:
                    elem.text = new_text
                    changed = True
            if elem.tail:
                new_tail = re.sub(r'&(?!lt;|gt;|amp;)', '&amp;', elem.tail)
                if new_tail != elem.tail:
                    elem.tail = new_tail
                    changed = True

        # 3️⃣ Controlla <numerusform> senza numerus="yes"
        numerus_children = message.findall('translation/numerusform')
        if numerus_children and message.attrib.get('numerus') != 'yes':
            message.attrib['numerus'] = 'yes'
            changed = True

    if changed:
        tree.write(path, encoding="utf-8", xml_declaration=True)
        print(f"✔ Corretto: {path}")
    else:
        print("  Nessuna modifica necessaria")

def main():
    ts_dir = pathlib.Path("translations")
    for ts_file in ts_dir.glob("*.ts"):
        fix_ts_file(ts_file)

if __name__ == "__main__":
    main()
