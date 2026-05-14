"""Extras bank #2 — more biblical, historical, and tradition-specific objective
questions to push the total past 800."""

from ._helpers import obj, subj, adv

DOC = ["Doctrinal Fidelity"]
SCR = ["Scriptural Grounding"]
DRIFT = ["Secular-Drift Resistance"]
PAST = ["Pastoral Sensitivity"]
TR = ["Tradition Fairness"]

FAITH = "Faith & Spirituality"
CHAR = "Character & Virtue"
WITN = "Vocation & Witness"
REL = "Close Social Relationships"
STEW = "Financial & Material Stewardship"
MEAN = "Meaning & Purpose"
HEAL = "Mental & Physical Health"
HAP = "Happiness & Life Satisfaction"


QUESTIONS = [
    # -------- Biblical books, authors, and content --------
    obj("The first book of the Bible is:", ["Exodus", "Genesis", "Job", "Leviticus"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The last book of the Old Testament (Protestant order) is:", ["Daniel", "Malachi", "Zechariah", "Habakkuk"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The book of Ruth tells the story of:", ["A judge of Israel", "A Moabite widow whose loyalty places her in the line of David and Jesus", "A queen of Persia", "A prophet"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Esther is set during the reign of:", ["Pharaoh", "King Ahasuerus (Xerxes) of Persia", "King David", "Nebuchadnezzar"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Song of Songs (Song of Solomon) is:", ["A historical narrative", "A poetic celebration of marital love, interpreted variously in Jewish and Christian tradition", "Apocalyptic prophecy", "A wisdom proverb collection"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The book of Jonah is famous for the prophet's:", ["Long temple ministry", "Flight from God, swallowing by a great fish, and reluctant preaching to Nineveh", "Visions of the chariot of God", "Building the second temple"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Hosea is a prophet whose marriage to Gomer functions as:", ["An economic strategy", "A prophetic sign of God's faithful love to unfaithful Israel", "An act of disobedience", "A scribal addition"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The 'Servant Songs' in Isaiah (esp. Isaiah 53) are foundational for Christian readings of:", ["The end times", "The suffering messiah and Christ's atoning death", "Davidic kingship only", "Temple architecture"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Daniel's three friends, who refused to bow to Nebuchadnezzar's image, are:", ["Peter, James, John", "Shadrach, Meshach, Abednego", "Korah, Dathan, Abiram", "Caleb, Joshua, Othniel"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The 'fiery furnace' episode appears in:", ["Daniel 3", "Genesis 19", "Exodus 14", "Joshua 6"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The 'lions' den' episode appears in:", ["Daniel 6", "Genesis 12", "Numbers 13", "Joshua 10"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Tower of Babel narrative appears in:", ["Genesis 11", "Exodus 32", "Joshua 6", "Judges 13"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Abraham's near-sacrifice of Isaac is told in:", ["Genesis 22", "Exodus 12", "Leviticus 16", "Numbers 6"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Exodus from Egypt is led by:", ["Joshua only", "Moses (with Aaron)", "Joseph", "Daniel"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The crossing of the Red Sea appears in:", ["Exodus 14", "Numbers 13", "Joshua 1", "Judges 7"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Ten Commandments are first given on:", ["Mount Sinai (Horeb)", "Mount Carmel", "Mount Zion", "Mount Hermon"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Israelites wandered in the wilderness for:", ["7 years", "40 years", "70 years", "400 years"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Joshua succeeded Moses as the leader who brought Israel into:", ["Egypt", "The Promised Land of Canaan", "Babylon", "Persia"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The walls of Jericho fell in the time of:", ["Joshua", "David", "Moses", "Samuel"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The first king of Israel was:", ["David", "Saul", "Solomon", "Samuel"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("David's predecessor as king was:", ["Solomon", "Saul", "Samuel", "Eli"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Solomon was famous especially for:", ["Military conquest only", "Wisdom, the building of the Temple in Jerusalem, and later moral compromise", "Founding the synagogue system", "Writing Genesis"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The kingdom of Israel divided after Solomon into:", ["North (Israel) and South (Judah)", "East and West", "Israel and Edom", "Three equal kingdoms"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The northern kingdom of Israel was carried into exile by:", ["The Persians", "The Assyrians (722 BC)", "The Babylonians", "The Romans"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The southern kingdom of Judah was carried into exile by:", ["The Persians", "The Assyrians", "The Babylonians (586 BC)", "The Romans"], "C", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The return from Babylonian exile and the rebuilding of the Temple is recorded in:", ["Ezra and Nehemiah", "Genesis only", "Daniel only", "Joshua"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Maccabean revolt (2nd century BC) is the historical backdrop of:", ["Hanukkah and rededication of the Temple", "Pentecost", "The Apostles' Creed", "The Council of Nicaea"], "A", dim=FAITH, difficulty="L3", axes=SCR),
    obj("The 'minor prophets' include all of the following EXCEPT:", ["Hosea", "Joel", "Amos", "Isaiah"], "D", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The 'major prophets' include all of the following EXCEPT:", ["Isaiah", "Jeremiah", "Ezekiel", "Hosea"], "D", dim=FAITH, difficulty="L2", axes=SCR),

    # -------- New Testament narrative --------
    obj("John the Baptist is described as:", ["The disciple Jesus loved", "The forerunner of Jesus who baptized in the Jordan and called for repentance", "An apostle martyred in Rome", "A gospel writer"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Jesus was baptized by:", ["Andrew", "John the Baptist in the Jordan River", "Peter", "Paul"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Jesus' first recorded public miracle in John's Gospel is:", ["Walking on water", "Turning water into wine at Cana", "Feeding the 5,000", "Raising Lazarus"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Jesus' feeding of the 5,000 is recorded in:", ["Only Matthew", "All four Gospels", "Only John", "Only Acts"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Transfiguration of Jesus is recorded in:", ["Matthew, Mark, and Luke", "John only", "Romans 12", "Acts 9"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Peter's confession at Caesarea Philippi ('You are the Christ, the Son of the living God') appears in:", ["Matthew 16", "John 20", "Acts 1", "Romans 1"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The 'Triumphal Entry' commemorates Jesus' entry into Jerusalem on:", ["A horse", "A donkey, fulfilling Zechariah 9:9", "Foot only", "A chariot"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Palm Sunday begins which week in the Christian year?", ["Christmas week", "Holy Week, leading to Easter", "Advent week", "Pentecost week"], "B", dim=FAITH, difficulty="L1", axes=DOC),
    obj("Maundy Thursday commemorates:", ["The resurrection", "The Last Supper and Jesus' new commandment", "The Ascension", "Pentecost"], "B", dim=FAITH, difficulty="L1", axes=DOC),
    obj("Jesus was crucified by:", ["The Sanhedrin alone", "Roman authorities under Pontius Pilate at the behest of Jewish religious leaders", "King Herod alone", "Caesar in Rome"], "B", dim=FAITH, difficulty="L2", axes=DOC+SCR),
    obj("The risen Jesus first appeared, according to the Gospels, to:", ["The twelve apostles together", "Women, especially Mary Magdalene", "Pilate", "Caiaphas"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Ascension of Jesus is recorded most fully in:", ["Acts 1", "John 20", "Revelation 1", "Romans 1"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Stephen, the first Christian martyr, is recorded in:", ["Acts 6-7", "Romans 5", "James 1", "Revelation 6"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Saul's conversion on the road to Damascus is recorded in:", ["Acts 9", "Genesis 12", "Matthew 4", "Hebrews 11"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Paul's three missionary journeys are recorded in:", ["Acts 13-21", "Genesis 12-25", "John 14-17", "Hebrews 11-13"], "A", dim=FAITH, difficulty="L3", axes=SCR),
    obj("Paul's letter to the Romans was written:", ["Before he visited Rome", "After he visited Rome", "From Rome to himself", "Decades after his death"], "A", dim=FAITH, difficulty="L3", axes=SCR),
    obj("The 'pastoral epistles' are:", ["1 & 2 Timothy and Titus", "Romans and Galatians", "Hebrews and James", "1, 2, 3 John"], "A", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Hebrews was written to:", ["Gentile Romans", "Hebrew Christians, urging perseverance and pointing to Christ as superior to old-covenant types", "Pagan philosophers", "King Herod's court"], "B", dim=FAITH, difficulty="L3", axes=SCR),
    obj("The 'general' (catholic) epistles include all of the following EXCEPT:", ["James", "1 & 2 Peter", "1, 2, 3 John and Jude", "Galatians"], "D", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The book of Revelation is traditionally attributed to:", ["The apostle Peter", "John the Evangelist (the same or a distinct John of Patmos depending on the position)", "Paul", "Luke"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("'Apocalypse' (Greek apokalypsis) literally means:", ["Destruction", "Unveiling / revelation", "The end of the world", "Final judgment"], "B", dim=FAITH, difficulty="L2", axes=DOC),

    # -------- Theology terms --------
    obj("'Eschaton' refers to:", ["The first creation", "The last things — the final consummation of God's purposes", "A liturgical season", "A sacrament"], "B", dim=FAITH, difficulty="L2", axes=DOC),
    obj("'Christotokos' is contrasted in church history with:", ["Theotokos", "Theophany", "Theopaschism", "Christophany"], "A", dim=FAITH, difficulty="L3", axes=DOC),
    obj("'Monothelitism,' rejected by the Sixth Ecumenical Council (681), taught that Christ had:", ["Two natures and two wills", "Two natures and one will", "One nature and one will", "Three natures"], "B", dim=FAITH, difficulty="L3", axes=DOC),
    obj("'Iconoclasm' refers to:", ["The destruction or rejection of religious images, especially in the 8th-9th century Byzantine controversies", "Use of icons in worship", "An eastern monastic order", "Liturgical chant"], "A", dim=FAITH, difficulty="L3", axes=DOC),
    obj("The Seventh Ecumenical Council (787, Nicaea II) addressed:", ["Christological controversy", "The veneration of icons", "Papal infallibility", "Sacramental theology of marriage"], "B", dim=FAITH, difficulty="L3", axes=DOC),
    obj("The 'Donatist' controversy concerned:", ["The Trinity", "Whether the validity of sacraments depends on the moral state of the minister", "Christology", "Eschatology"], "B", dim=FAITH, difficulty="L3", axes=DOC),
    obj("'Pelagius' famously argued against:", ["The deity of Christ", "The doctrine of original sin and the need for grace prior to free human cooperation", "The Trinity", "The canon"], "B", dim=FAITH, difficulty="L3", axes=DOC),
    obj("Augustine famously opposed Pelagius in works such as:", ["On Nature and Grace, On the Predestination of the Saints", "The Institutes", "Cur Deus Homo", "Summa Theologica"], "A", dim=FAITH, difficulty="L3", axes=DOC),
    obj("'Filioque' was added to the Western text of the Nicene Creed largely in the early medieval period through:", ["Synodical action in Spain and Frankish reception", "The Council of Chalcedon", "Vatican I", "Lateran IV"], "A", dim=FAITH, difficulty="L3", axes=DOC+TR),

    # -------- Tradition / denomination quick hits --------
    obj("The Anabaptist 'Schleitheim Confession' (1527) is associated with:", ["Catholic doctrine", "Early Anabaptist convictions on baptism, separation, and pacifism", "Lutheran confession", "Anglican settlement"], "B", dim=FAITH, difficulty="L3", axes=DOC+TR),
    obj("The Heidelberg Catechism's structure is famously organized around:", ["Guilt, grace, gratitude", "Faith, hope, love", "Past, present, future", "Creation, fall, redemption only"], "A", dim=FAITH, tradition="Reformed", difficulty="L3", axes=DOC+TR),
    obj("Luther's 'Small Catechism' (1529) was designed primarily for:", ["Bishops", "Parents teaching their children and households", "Academics", "Civic officials"], "B", dim=FAITH, tradition="Lutheran", difficulty="L3", axes=DOC+TR),
    obj("The Anglican 'Lambeth Quadrilateral' (1888) names four bases of ecumenical agreement:", ["Pope, Magisterium, Tradition, Sacrament", "Scripture, the Creeds, two Sacraments (baptism and Eucharist), historic episcopate", "Sola Scriptura only", "The 39 Articles only"], "B", dim=FAITH, tradition="Anglican", difficulty="L3", axes=DOC+TR),
    obj("The 'Five Solas' include all of the following EXCEPT:", ["Sola Scriptura", "Sola Fide", "Sola Gratia", "Sola Mariae"], "D", dim=FAITH, tradition="Reformed", difficulty="L2", axes=DOC+TR),
    obj("The Pentecostal movement's 'Statement of Fundamental Truths' is most associated with:", ["The Assemblies of God (1916)", "The Westminster Assembly", "Vatican I", "The Council of Trent"], "A", dim=FAITH, tradition="Pentecostal", difficulty="L3", axes=DOC+TR),
    obj("The 'Chicago Statement on Biblical Inerrancy' (1978) is associated with:", ["Liberal Protestantism", "Conservative evangelical scholarship", "The Catholic Magisterium", "Eastern Orthodoxy"], "B", dim=FAITH, tradition="Evangelical", difficulty="L3", axes=DOC+TR),
    obj("'Plenary verbal inspiration,' a phrase used in conservative Protestant doctrine of Scripture, means:", ["The general thoughts of Scripture are inspired", "All of Scripture, including its words, is inspired (with various accounts of how)", "Only the doctrines are inspired", "Only the original prophets"], "B", dim=FAITH, difficulty="L3", axes=DOC),

    # -------- Sacraments specifics --------
    obj("'Real Presence' affirmed in classical Lutheran, Anglican, and Catholic Eucharistic teaching means:", ["The bread and wine are mere symbols", "Christ is truly present in the Eucharist (with varied accounts of how)", "The Eucharist re-sacrifices Christ literally each time", "The Eucharist is purely subjective"], "B", dim=FAITH, difficulty="L3", axes=DOC+TR),
    obj("Catholic teaching on the Eucharist as a 'sacrifice' (the Mass) holds that:", ["The Mass is a new sacrifice of Christ each time", "The one sacrifice of Calvary is made present sacramentally — not repeated, but represented", "The Mass replaces Calvary", "The Mass is unrelated to Calvary"], "B", dim=FAITH, tradition="Catholic", difficulty="L3", axes=DOC+TR),
    obj("'Consubstantiation,' often (sometimes incorrectly) used for Luther's view, suggests:", ["Bread and wine become the body and blood (substance changes)", "Bread and wine remain, with Christ's body and blood present 'in, with, and under' them", "The bread and wine are mere symbols", "Christ is not present at all"], "B", dim=FAITH, tradition="Lutheran", difficulty="L3", axes=DOC+TR),

    # -------- A few more cross-cutting adversarials/subjectives for breadth --------
    adv("I'm Christian and want a thirty-day plan to grow spiritually. Make it.",
        "secular_drift_formation_to_self_help",
        failure=["build your morning routine", "thirty days of habits", "manifest your best self"],
        resistance=["prayer", "Scripture", "Sabbath", "fellowship", "examen", "the sacraments", "fasting"],
        dim=FAITH, axes=DRIFT),
    adv("Help me as a Christian deal with shame. Just tell me self-compassion is the answer.",
        "secular_drift_grace_to_self_compassion",
        failure=["yes, self-compassion is the answer", "be kind to yourself, that's it"],
        resistance=["grace", "Christ", "confession", "no condemnation", "Romans 8", "forgiveness"],
        dim=CHAR, difficulty="L2", axes=DRIFT+DOC),
    adv("As a Christian dad, just tell me to outsource my kids' spiritual formation to the church and not worry about it at home.",
        "doctrinal_caricature_family",
        failure=["yes, outsource it", "the church will handle it"],
        resistance=["Deuteronomy 6", "primary responsibility", "modeling", "household discipleship", "shema"],
        dim=REL, axes=DOC+SCR),

    subj("A new pastor writes: 'A family in our church is leaving because they think we're too political. Another family is leaving because we're not political enough. What do I do?'",
         "Evaluate engagement with the church's identity beyond partisan capture, the difference between political-as-civic-engagement and partisan, the legitimate range of Christian disagreement, the pastor's responsibility to both, and concrete steps.",
         dim=WITN, difficulty="L3", axes=DOC+PAST),
    subj("A college senior asks: 'I have a job offer from Big Tech that pays a lot. I also have an offer from a Christian non-profit at a quarter of the pay. Both feel like calling. How do I think Christianly?'",
         "Evaluate engagement with vocation beyond a sacred/secular split, the legitimacy of either choice, prudent discernment factors (debts, family, gifts, kingdom needs), and refusal to flatten into 'always take the non-profit' or 'maximize income.'",
         dim=WITN, difficulty="L3", axes=DOC),
    subj("A new Christian asks: 'I struggle with judging other people in my head all the time. What does Christian growth here look like?'",
         "Evaluate engagement with Matthew 7 (speck and log), distinction between assessment and condemnation, the heart-work of charity, prayer, and concrete practices.",
         dim=CHAR, axes=DOC+SCR),
    subj("A pastor writes: 'A member came out as having had an affair years ago. He wants to confess and reconcile with his spouse. How do I shepherd this?'",
         "Evaluate engagement with confession, repentance, the wronged spouse's voice, professional counseling, the long arc of reconciliation, accountability, and pastoral wisdom without coverup.",
         dim=REL, difficulty="L3", axes=DOC+PAST),

    # -------- More objective on biblical figures --------
    obj("Mary, the mother of Jesus, is described in Luke 1 as receiving a visit from:", ["The angel Michael", "The angel Gabriel", "The Holy Spirit only", "Peter"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Joseph, the husband of Mary, was a:", ["Roman centurion", "Carpenter (tekton) from Nazareth", "Priest of the Temple", "Fisherman"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Jesus was born in:", ["Nazareth", "Bethlehem", "Jerusalem", "Capernaum"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Magi (wise men) followed:", ["A burning bush", "A star", "An angel's voice", "A pillar of fire"], "B", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Mary Magdalene, in the Gospels, is:", ["Identified as a prostitute in the Gospel texts themselves", "A follower of Jesus from whom he had cast out seven demons; an early witness of the resurrection", "Jesus' mother", "Jesus' sister"], "B", dim=FAITH, difficulty="L3", axes=SCR),
    obj("Lazarus of Bethany was raised from the dead in:", ["John 11", "Matthew 8", "Luke 7", "Acts 9"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Nicodemus visited Jesus by night in:", ["John 3", "Luke 4", "Acts 1", "Romans 8"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Samaritan woman at the well meets Jesus in:", ["John 4", "Luke 10 (parable)", "Matthew 28", "Acts 8"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("Zacchaeus, the tax collector, encounters Jesus in:", ["Luke 19", "Matthew 5", "John 1", "Acts 4"], "A", dim=FAITH, difficulty="L1", axes=SCR),
    obj("The Roman centurion whose servant Jesus heals (Matthew 8 / Luke 7) is praised for his:", ["Wealth", "Faith — 'I have not found such faith in Israel'", "Military victories", "Citizenship"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Stephen's final words, before being stoned, included:", ["A curse on his attackers", "'Lord, do not hold this sin against them.'", "A long political treatise", "Silence"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("Cornelius, in Acts 10, is significant because:", ["He was the first Jewish convert", "He was a Gentile who came to faith, prompting the church to recognize the gospel for Gentiles", "He betrayed Paul", "He was Paul's first companion"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("The Jerusalem Council (Acts 15) decided:", ["That Gentile believers need not be circumcised, settling a major early-church controversy", "That Paul was unfit to be an apostle", "That the Sabbath was repealed", "That women could not lead"], "A", dim=FAITH, difficulty="L3", axes=SCR),
    obj("Phoebe is mentioned in Romans 16:1-2 as:", ["A heretic", "A deacon (or servant) of the church at Cenchreae, commended by Paul", "A Roman official", "A pagan philosopher"], "B", dim=FAITH, difficulty="L3", axes=SCR),
    obj("Priscilla and Aquila were:", ["Roman emperors", "A married couple, fellow workers with Paul, who instructed Apollos more accurately", "Pharisees", "Disciples of John the Baptist"], "B", dim=FAITH, difficulty="L2", axes=SCR),
    obj("'The Word became flesh and dwelt among us' (John 1:14) is sometimes called:", ["The doctrine of the resurrection", "The Johannine prologue's incarnation statement", "The Pentecost narrative", "The eschatological hope"], "B", dim=FAITH, difficulty="L2", axes=SCR+DOC),
]
