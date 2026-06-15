#!/usr/bin/env python3
"""
Generate the Greek translation catalog for Art on Pressies.

This project runs on Windows / a slim Docker image where the GNU `gettext`
tools (xgettext / msgfmt) are not available, so we can't use Django's
`makemessages` / `compilemessages`. Instead this script is the single source
of truth for the Greek strings and writes BOTH:

    locale/el/LC_MESSAGES/django.po   (human-editable, for future tooling)
    locale/el/LC_MESSAGES/django.mo   (binary, what Django loads at runtime)

To add/edit a translation: change SINGULAR / PLURALS below and re-run:

    python build_locale.py

No third-party packages required (pure stdlib: struct, array, os).
"""

import array
import os
import struct

LANG = 'el'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'locale', LANG, 'LC_MESSAGES')

HEADER = (
    "Project-Id-Version: art_on_pressies\n"
    "Report-Msgid-Bugs-To: \n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Language: el\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
)

# ── Singular messages: english source -> greek translation ──────────────────
SINGULAR = {
    # ── Navigation / footer / common ──
    "Home": "Αρχική",
    "Gallery": "Συλλογή",
    "About": "Σχετικά",
    "Cart": "Καλάθι",
    "Contact": "Επικοινωνία",
    "Get in Touch": "Επικοινωνία",
    "Search...": "Αναζήτηση...",
    "Search designs...": "Αναζήτηση σχεδίων...",
    "Quick Links": "Γρήγοροι σύνδεσμοι",
    "Ready for your dream nails?": "Έτοιμη για τα νύχια των ονείρων σου;",
    "Enquire Now": "Ρώτησέ μας",
    "All rights reserved.": "Με επιφύλαξη παντός δικαιώματος.",
    "Handcrafted press-on nails designed to make every set a wearable work of art.":
        "Χειροποίητα press-on νύχια, σχεδιασμένα ώστε κάθε σετ να είναι ένα φορετό έργο τέχνης.",

    # ── Home ──
    "Handcrafted Press-On Nails": "Χειροποίητα Press-On Νύχια",
    "Nails That Are Works of Art": "Νύχια που Είναι Έργα Τέχνης",
    "Handcrafted press-on nails designed with love. Every set is unique, elegant, and made to turn heads.":
        "Χειροποίητα press-on νύχια, φτιαγμένα με αγάπη. Κάθε σετ είναι μοναδικό, κομψό και φτιαγμένο για να τραβάει τα βλέμματα.",
    "View Gallery": "Δες τη Συλλογή",
    "Custom Order": "Παραγγελία στα Μέτρα σου",
    "Featured Designs": "Ξεχωριστά Σχέδια",
    "Our latest and most-loved creations": "Οι πιο πρόσφατες και αγαπημένες μας δημιουργίες",
    "See All Designs": "Δες Όλα τα Σχέδια",
    "Got a Vision?": "Έχεις μια Ιδέα;",
    "Whether you have a specific design in mind or want us to surprise you — we'd love to create your perfect set.":
        "Είτε έχεις ένα συγκεκριμένο σχέδιο στο μυαλό σου είτε θες να σε εκπλήξουμε — θα χαρούμε πολύ να δημιουργήσουμε το τέλειο σετ για σένα.",
    "Let's Talk Nails": "Ας Μιλήσουμε για Νύχια",

    # ── Gallery ──
    "Our Gallery": "Η Συλλογή μας",
    "Browse our collection of handcrafted press-on nail designs":
        "Περιήγησε στη συλλογή μας με χειροποίητα σχέδια press-on νυχιών",
    "All": "Όλα",
    "No designs found in \"%(name)s\".": "Δεν βρέθηκαν σχέδια στην κατηγορία \"%(name)s\".",
    "No designs found.": "Δεν βρέθηκαν σχέδια.",
    "View all designs": "Δες όλα τα σχέδια",

    # ── About ──
    "About Us": "Σχετικά με Εμάς",
    "The story behind the art": "Η ιστορία πίσω από την τέχνη",
    "was born from a love of creativity and self-expression. What started as a hobby — painting tiny canvases on press-on nails — quickly grew into a passion project dedicated to crafting wearable art for every occasion.":
        "γεννήθηκε από την αγάπη για τη δημιουργικότητα και την αυτοέκφραση. Αυτό που ξεκίνησε ως χόμπι — ζωγραφική σε μικροσκοπικούς καμβάδες πάνω σε press-on νύχια — γρήγορα εξελίχθηκε σε ένα project με μεράκι, αφιερωμένο στη δημιουργία φορετής τέχνης για κάθε περίσταση.",
    "Every set is designed and handcrafted with care. From bold graphic patterns to delicate detailed work, we believe your nails should be as unique as you are. No two sets are ever exactly the same.":
        "Κάθε σετ σχεδιάζεται και φτιάχνεται στο χέρι με φροντίδα. Από τολμηρά γραφικά μοτίβα μέχρι λεπτεπίλεπτες λεπτομέρειες, πιστεύουμε ότι τα νύχια σου πρέπει να είναι τόσο μοναδικά όσο κι εσύ. Κανένα σετ δεν είναι ποτέ ακριβώς ίδιο με κάποιο άλλο.",
    "We use high-quality materials and take pride in creating press-ons that not only look stunning but are comfortable, durable, and easy to apply at home.":
        "Χρησιμοποιούμε υλικά υψηλής ποιότητας και είμαστε περήφανοι που δημιουργούμε press-on νύχια που όχι μόνο δείχνουν εντυπωσιακά, αλλά είναι και άνετα, ανθεκτικά και εύκολα στην εφαρμογή στο σπίτι.",
    "What We Stand For": "Οι Αξίες μας",
    "Made with Love": "Φτιαγμένα με Αγάπη",
    "Every set is handcrafted with attention to detail and genuine passion.":
        "Κάθε σετ είναι χειροποίητο, με προσοχή στη λεπτομέρεια και γνήσιο πάθος.",
    "Unique Designs": "Μοναδικά Σχέδια",
    "Original art on every nail — no mass production, no copies.":
        "Πρωτότυπη τέχνη σε κάθε νύχι — χωρίς μαζική παραγωγή, χωρίς αντίγραφα.",
    "Quality First": "Ποιότητα Πάνω απ' Όλα",
    "Premium materials for nails that last and feel amazing.":
        "Premium υλικά για νύχια που διαρκούν και είναι υπέροχα στην αίσθηση.",
    "Ready to Get Started?": "Έτοιμη να Ξεκινήσεις;",
    "Browse our gallery or get in touch for a custom set.":
        "Περιήγησε στη συλλογή μας ή επικοινώνησε μαζί μας για ένα δικό σου σετ.",

    # ── Contact ──
    "Get in <span class=\"text-petal\">Touch</span>": "<span class=\"text-petal\">Επικοινωνία</span>",
    "Have a design in mind? Want a custom set? Drop us a message and we'll get back to you.":
        "Έχεις ένα σχέδιο στο μυαλό σου; Θες ένα δικό σου σετ; Στείλε μας μήνυμα και θα σου απαντήσουμε.",
    "Send Enquiry": "Αποστολή Μηνύματος",

    # ── Search ──
    "Search": "Αναζήτηση",
    "Search Results": "Αποτελέσματα Αναζήτησης",
    "Results for \"<span class=\"text-grape font-semibold\">%(query)s</span>\"":
        "Αποτελέσματα για \"<span class=\"text-grape font-semibold\">%(query)s</span>\"",
    "No designs found for \"%(query)s\".": "Δεν βρέθηκαν σχέδια για \"%(query)s\".",
    "Browse all designs": "Δες όλα τα σχέδια",
    "Enter a search term above to find designs.":
        "Πληκτρολόγησε έναν όρο αναζήτησης παραπάνω για να βρεις σχέδια.",

    # ── Cart ──
    "Your Cart": "Το Καλάθι σου",
    "Shape:": "Σχήμα:",
    "Size:": "Μέγεθος:",
    "Custom": "Προσαρμοσμένο",
    "(€%(price)s each)": "(€%(price)s το καθένα)",
    "Remove": "Αφαίρεση",
    "Subtotal": "Υποσύνολο",
    "Continue Shopping": "Συνέχεια Αγορών",
    "Proceed to Checkout": "Ολοκλήρωση Παραγγελίας",
    "Your cart is empty": "Το καλάθι σου είναι άδειο",
    "Browse the gallery and add something you love.":
        "Περιήγησε στη συλλογή και πρόσθεσε κάτι που αγαπάς.",
    "Browse Gallery": "Δες τη Συλλογή",

    # ── Checkout ──
    "Checkout": "Ολοκλήρωση Αγοράς",
    "Order Summary": "Σύνοψη Παραγγελίας",
    "Review your selections before getting in touch": "Έλεγξε τις επιλογές σου πριν προχωρήσεις",
    "Your Items": "Τα Προϊόντα σου",
    "Shipping (Greece)": "Αποστολή (Ελλάδα)",
    "Total": "Σύνολο",
    "Delivery Method": "Τρόπος Παράδοσης",
    "Locker pickup": "Παραλαβή από locker",
    "Courier": "Κούριερ",
    "Home delivery": "Παράδοση στο σπίτι",
    "Pay securely with your card via Stripe. We ship within Greece.":
        "Πλήρωσε με ασφάλεια με την κάρτα σου μέσω Stripe. Αποστέλλουμε εντός Ελλάδας.",
    "Pay with Card": "Πληρωμή με Κάρτα",
    "Have a question first?": "Έχεις πρώτα κάποια ερώτηση;",
    "Send an enquiry instead": "Στείλε μας μήνυμα",
    "Back to Cart": "Πίσω στο Καλάθι",

    # ── Checkout success ──
    "Thank you!": "Ευχαριστούμε!",
    "Thank You!": "Ευχαριστούμε!",
    "Your order is on its way to us.": "Λάβαμε την παραγγελία σου.",
    "Order #%(id)s received": "Η παραγγελία #%(id)s λήφθηκε",
    "We've received your payment and sent a confirmation to <span class=\"font-semibold text-plum\">%(email)s</span>.":
        "Λάβαμε την πληρωμή σου και στείλαμε επιβεβαίωση στο <span class=\"font-semibold text-plum\">%(email)s</span>.",
    "We've received your payment.": "Λάβαμε την πληρωμή σου.",
    "We'll be in touch shortly to confirm finishing details and shipping timeline.":
        "Θα επικοινωνήσουμε σύντομα μαζί σου για να επιβεβαιώσουμε τις τελευταίες λεπτομέρειες και τον χρόνο αποστολής.",
    "View order status": "Δες την κατάσταση παραγγελίας",
    "Payment received": "Η πληρωμή ελήφθη",
    "Thanks for your order — we'll be in touch shortly.":
        "Ευχαριστούμε για την παραγγελία σου — θα επικοινωνήσουμε σύντομα μαζί σου.",
    "Back to Gallery": "Πίσω στη Συλλογή",

    # ── Checkout cancel ──
    "Payment cancelled": "Η πληρωμή ακυρώθηκε",
    "No worries — your cart is still saved. You can finish checkout whenever you're ready.":
        "Μην ανησυχείς — το καλάθι σου είναι αποθηκευμένο. Μπορείς να ολοκληρώσεις την αγορά όποτε είσαι έτοιμη.",

    # ── Order tracking ──
    "Order #%(id)s": "Παραγγελία #%(id)s",
    "Track your order status": "Παρακολούθησε την κατάσταση της παραγγελίας σου",
    "Status": "Κατάσταση",
    "We're preparing your nails — we'll be in touch shortly.":
        "Ετοιμάζουμε τα νύχια σου — θα επικοινωνήσουμε σύντομα μαζί σου.",
    "On its way!": "Καθ' οδόν!",
    "Your parcel has been handed to the courier.":
        "Το δέμα σου παραδόθηκε στην εταιρεία ταχυμεταφορών.",
    "Delivered": "Παραδόθηκε",
    "Your order has been delivered. Enjoy!": "Η παραγγελία σου παραδόθηκε. Καλή απόλαυση!",
    "Pending": "Σε εκκρεμότητα",
    "Cancelled": "Ακυρώθηκε",
    "Failed": "Απέτυχε",
    "Delivery via": "Παράδοση μέσω",
    "Tracking": "Παρακολούθηση",
    "Track with courier": "Παρακολούθηση μέσω courier",
    "Total paid": "Σύνολο πληρωμής",

    # ── Design detail ──
    "Shape": "Σχήμα",
    "Size": "Μέγεθος",
    "Need help sizing?": "Χρειάζεσαι βοήθεια με το μέγεθος;",
    "thumb · index · middle · ring · pinky": "αντίχειρας · δείκτης · μέσος · παράμεσος · μικρό",
    "Hover a size to see per-finger measurements.":
        "Πέρασε τον δείκτη πάνω από ένα μέγεθος για να δεις τις διαστάσεις ανά δάχτυλο.",
    "Add to Cart": "Προσθήκη στο Καλάθι",
    "Enquire About This Design": "Ρώτησε για αυτό το Σχέδιο",
    "More %(cat)s": "Περισσότερα: %(cat)s",
    "How to Find Your Size": "Πώς να Βρεις το Μέγεθός σου",
    "Sizing instructions": "Οδηγίες μεγέθους",
    "Custom Size": "Προσαρμοσμένο Μέγεθος",
    "Choose a width (mm) for each finger.": "Επίλεξε πλάτος (mm) για κάθε δάχτυλο.",
    "Confirm Custom Size": "Επιβεβαίωση Προσαρμοσμένου Μεγέθους",

    # ── Forms ──
    "Name": "Όνομα",
    "Email": "Email",
    "Phone": "Τηλέφωνο",
    "Design": "Σχέδιο",
    "Message": "Μήνυμα",
    "Your name": "Το όνομά σου",
    "Phone number (optional)": "Αριθμός τηλεφώνου (προαιρετικό)",
    "Tell us about your dream nails...": "Πες μας για τα νύχια των ονείρων σου...",

    # ── Views (flash messages, finger labels, Stripe) ──
    "Thumb": "Αντίχειρας",
    "Index": "Δείκτης",
    "Middle": "Μέσος",
    "Ring": "Παράμεσος",
    "Pinky": "Μικρό",
    "\"%(title)s\" added to your cart.": "Το \"%(title)s\" προστέθηκε στο καλάθι σου.",
    "Thanks for your enquiry! We'll get back to you soon.":
        "Ευχαριστούμε για το μήνυμά σου! Θα επικοινωνήσουμε σύντομα μαζί σου.",
    "Shape: %(value)s": "Σχήμα: %(value)s",
    "Size: %(value)s": "Μέγεθος: %(value)s",
    "Standard shipping (Greece)": "Τυπική αποστολή (Ελλάδα)",

    # ── Cookie notice ──
    "We use only essential cookies to keep your cart and language preference working. No tracking, no ads.":
        "Χρησιμοποιούμε μόνο απαραίτητα cookies για να λειτουργούν το καλάθι και η προτίμηση γλώσσας σου. Χωρίς παρακολούθηση, χωρίς διαφημίσεις.",
    "Got it": "Εντάξει",
    "Learn more": "Μάθε περισσότερα",

    # ── Privacy & Cookies page ──
    "Privacy & Cookies": "Απόρρητο & Cookies",
    "How we handle your information": "Πώς διαχειριζόμαστε τις πληροφορίες σου",
    "Art on Pressies is a small, owner-run business. We collect only what we need to process your orders and answer your enquiries — nothing more. We don't sell your data, and we don't use advertising or tracking cookies.":
        "Το Art on Pressies είναι μια μικρή επιχείρηση που τη διαχειρίζεται η ίδια η ιδιοκτήτρια. Συλλέγουμε μόνο όσα χρειαζόμαστε για να επεξεργαστούμε τις παραγγελίες σου και να απαντήσουμε στα μηνύματά σου — τίποτα παραπάνω. Δεν πουλάμε τα δεδομένα σου και δεν χρησιμοποιούμε cookies διαφήμισης ή παρακολούθησης.",
    "Cookies we use": "Τα cookies που χρησιμοποιούμε",
    "We use a small number of essential cookies that keep the site working. These don't track you across other websites.":
        "Χρησιμοποιούμε έναν μικρό αριθμό απαραίτητων cookies που κρατούν τον ιστότοπο λειτουργικό. Αυτά δεν σε παρακολουθούν σε άλλους ιστότοπους.",
    "Cookie": "Cookie",
    "Purpose": "Σκοπός",
    "Duration": "Διάρκεια",
    "Keeps your shopping cart and your session": "Κρατά το καλάθι αγορών και τη συνεδρία σου",
    "Protects forms from cross-site request forgery":
        "Προστατεύει τις φόρμες από επιθέσεις cross-site request forgery",
    "Remembers your language choice (English or Greek)":
        "Θυμάται την επιλογή γλώσσας σου (Αγγλικά ή Ελληνικά)",
    "2 weeks": "2 εβδομάδες",
    "1 year": "1 έτος",
    "We also keep a small flag in your browser's local storage to remember that you've dismissed the cookie notice. It never leaves your device.":
        "Αποθηκεύουμε επίσης μια μικρή ένδειξη στον τοπικό αποθηκευτικό χώρο (local storage) του browser σου, ώστε να θυμόμαστε ότι έκλεισες αυτή την ειδοποίηση. Δεν φεύγει ποτέ από τη συσκευή σου.",
    "Information we collect": "Πληροφορίες που συλλέγουμε",
    "When you place an order, our payment provider collects your name, email address, and shipping address so we can deliver your nails and send you order updates.":
        "Όταν κάνεις μια παραγγελία, ο πάροχος πληρωμών μας συλλέγει το όνομα, το email και τη διεύθυνση αποστολής σου, ώστε να μπορούμε να σου παραδώσουμε τα νύχια σου και να σου στέλνουμε ενημερώσεις για την παραγγελία.",
    "When you send an enquiry, we keep the name, email, phone number (if given), and message you submit, so we can reply.":
        "Όταν μας στέλνεις ένα μήνυμα, κρατάμε το όνομα, το email, τον αριθμό τηλεφώνου (αν τον δώσεις) και το μήνυμα που υποβάλλεις, ώστε να μπορούμε να σου απαντήσουμε.",
    "Payments": "Πληρωμές",
    "Card payments are processed securely by Stripe. We never see or store your full card details.":
        "Οι πληρωμές με κάρτα διεκπεραιώνονται με ασφάλεια από τη Stripe. Δεν βλέπουμε ούτε αποθηκεύουμε ποτέ τα πλήρη στοιχεία της κάρτας σου.",
    "See how Stripe handles payment data": "Δες πώς η Stripe διαχειρίζεται τα δεδομένα πληρωμών",
    "Questions?": "Ερωτήσεις;",
    "If you'd like to know what data we hold about you, or want it removed, just get in touch and we'll help.":
        "Αν θέλεις να μάθεις ποια δεδομένα διατηρούμε για σένα, ή να ζητήσεις τη διαγραφή τους, απλώς επικοινώνησε μαζί μας και θα σε βοηθήσουμε.",
    "Last updated": "Τελευταία ενημέρωση",
}

# ── Plural messages: (singular_src, plural_src) -> [greek_singular, greek_plural] ──
PLURALS = {
    ("%(counter)s item", "%(counter)s items"):
        ["%(counter)s αντικείμενο", "%(counter)s αντικείμενα"],
    ("Subtotal (%(counter)s item)", "Subtotal (%(counter)s items)"):
        ["Υποσύνολο (%(counter)s αντικείμενο)", "Υποσύνολο (%(counter)s αντικείμενα)"],
}


def po_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def write_po(path):
    lines = ['msgid ""', 'msgstr ""']
    for hline in HEADER.split('\n'):
        if hline:
            lines.append('"%s\\n"' % po_escape(hline))
    lines.append('')

    for src in sorted(SINGULAR):
        lines.append('msgid "%s"' % po_escape(src))
        lines.append('msgstr "%s"' % po_escape(SINGULAR[src]))
        lines.append('')

    for (sing, plur), trans in sorted(PLURALS.items()):
        lines.append('msgid "%s"' % po_escape(sing))
        lines.append('msgid_plural "%s"' % po_escape(plur))
        lines.append('msgstr[0] "%s"' % po_escape(trans[0]))
        lines.append('msgstr[1] "%s"' % po_escape(trans[1]))
        lines.append('')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def write_mo(path):
    # Build the {key_bytes: value_bytes} catalog, including the "" header entry.
    catalog = {b'': HEADER.encode('utf-8')}
    for src, trans in SINGULAR.items():
        catalog[src.encode('utf-8')] = trans.encode('utf-8')
    for (sing, plur), trans in PLURALS.items():
        key = sing.encode('utf-8') + b'\x00' + plur.encode('utf-8')
        catalog[key] = b'\x00'.join(t.encode('utf-8') for t in trans)

    keys = sorted(catalog.keys())
    offsets = []
    ids = b''
    strs = b''
    for key in keys:
        val = catalog[key]
        offsets.append((len(ids), len(key), len(strs), len(val)))
        ids += key + b'\x00'
        strs += val + b'\x00'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]

    output = struct.pack(
        'Iiiiiii',
        0x950412de,          # magic
        0,                   # version
        len(keys),           # number of entries
        7 * 4,               # offset of key table
        7 * 4 + len(keys) * 8,  # offset of value table
        0, 0,                # hash table size + offset (unused)
    )
    output += array.array('i', koffsets + voffsets).tobytes()
    output += ids
    output += strs

    with open(path, 'wb') as f:
        f.write(output)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    po_path = os.path.join(OUT_DIR, 'django.po')
    mo_path = os.path.join(OUT_DIR, 'django.mo')
    write_po(po_path)
    write_mo(mo_path)
    total = len(SINGULAR) + len(PLURALS)
    print(f'Wrote {total} messages to:')
    print(f'  {po_path}')
    print(f'  {mo_path}')


if __name__ == '__main__':
    main()
