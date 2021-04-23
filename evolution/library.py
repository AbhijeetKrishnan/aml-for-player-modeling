lib_top_left = [
    "##\n"
    "# \n",

    "##\n"
    "##\n",

    "##\n"
    "#@\n",

    "##\n"
    "#.\n"
]

lib_top_right = [
    "##\n"
    " #\n",

    "##\n"
    "##\n",

    "##\n"
    "@#\n",

    "##\n"
    ".#\n"
]

lib_bottom_left = [
    "# \n"
    "##\n",

    "##\n"
    "##\n",

    "#@\n"
    "##\n",

    "#.\n"
    "##\n"
]

lib_bottom_right = [
    " #\n"
    "##\n",

    "##\n"
    "##\n",

    "@#\n"
    "##\n",

    ".#\n"
    "##\n"
]

lib_left = [
    "# \n"
    "# \n",

    "#@\n"
    "# \n",

    "# \n"
    "#@\n",

    "#.\n"
    "# \n",

    "# \n"
    "#.\n",

    "#.\n"
    "#.\n",

    "##\n"
    "#@\n",

    "#@\n"
    "##\n",

    "##\n"
    "#.\n",

    "#.\n"
    "##\n",

    "#@\n"
    "#.\n",

    "#.\n"
    "#@\n"
]

lib_right = [
    " #\n"
    " #\n",

    "@#\n"
    " #\n",

    " #\n"
    "@#\n",

    ".#\n"
    " #\n",

    " #\n"
    ".#\n",

    ".#\n"
    ".#\n",

    "##\n"
    "@#\n",

    "@#\n"
    "##\n",

    "##\n"
    ".#\n",

    ".#\n"
    "##\n",

    "@#\n"
    ".#\n",

    ".#\n"
    "@#\n"
]

lib_top = [
    "##\n"
    "  \n",

    "##\n"
    "@ \n",

    "##\n"
    " @\n",

    "##\n"
    ". \n",

    "##\n"
    " .\n",

    "##\n"
    "..\n",

    "##\n"
    "@#\n",

    "##\n"
    "#@\n",

    "##\n"
    ".#\n",

    "##\n"
    "#.\n",

    "##\n"
    "@.\n",

    "##\n"
    ".@\n"
]

lib_bottom = [
    "  \n"
    "##\n",

    "@ \n"
    "##\n",

    " @\n"
    "##\n",

    ". \n"
    "##\n",

    " .\n"
    "##\n",

    "..\n"
    "##\n",

    "@#\n"
    "##\n",

    "#@\n"
    "##\n",

    ".#\n"
    "##\n",

    "#.\n"
    "##\n",

    "@.\n"
    "##\n",

    ".@\n"
    "##\n"
]

# lib_center = [
#     "  \n"
#     "  \n",
#
#     "# \n"
#     "  \n",
#
#     "##\n"
#     "  \n",
#
#     "# \n"
#     "# \n",
#
#     "# \n"
#     " #\n",
#
#     " #\n"
#     "  \n",
#
#     " #\n"
#     "# \n",
#
#     " #\n"
#     " #\n",
#
#     "  \n"
#     "# \n",
#
#     "  \n"
#     "##\n",
#
#     "  \n"
#     " #\n",
#
#     "$ \n"
#     "  \n",
#
#     " $\n"
#     "  \n",
#
#     "  \n"
#     "$ \n",
#
#     "  \n"
#     " $\n",
#
#     "$ \n"
#     " $\n",
#
#     " $\n"
#     "$ \n",
#
#     ". \n"
#     "  \n",
#
#     "..\n"
#     "  \n",
#
#     ". \n"
#     ". \n",
#
#     ". \n"
#     " .\n",
#
#     " .\n"
#     "  \n",
#
#     " .\n"
#     ". \n",
#
#     " .\n"
#     " .\n",
#
#     "  \n"
#     ". \n",
#
#     "  \n"
#     "..\n",
#
#     "  \n"
#     " .\n",
#
#     "@ \n"
#     "  \n",
#
#     " @\n"
#     "  \n",
#
#     "  \n"
#     "@ \n",
#
#     "  \n"
#     " @\n",
#
#     "# \n"
#     "  \n",
# ]

def format_block(ls):
    return ls[0] + ls[1] + '\n' + ls[2] + ls[3] + '\n'

def lib_center():
    lib = [
        "  \n"
        "  \n"
    ]
    standard_block = [' ', ' ', ' ', ' ']

    # Single wall
    for i in range(4):
        new_block = standard_block.copy()
        new_block[i] = '#'
        lib.append(format_block(new_block))

    # Two walls
    for i in range(4):
        for j in range(i, 4):
            new_block = standard_block.copy()
            new_block[i] = '#'
            new_block[j] = '#'
            lib.append(format_block(new_block))

    # Player
    for i in range(4):
        new_block = standard_block.copy()
        new_block[i] = '@'
        lib.append(format_block(new_block))

    # Single stone
    for i in range(4):
        new_block = standard_block.copy()
        new_block[i] = '$'
        lib.append(format_block(new_block))

    # Two stones
    # Don't have two stones directly adjacent
    lib.append(
        "$ \n"
        " $\n"
    )
    lib.append(
        " $\n"
        "$ \n"
    )

    # Single goal
    for i in range(4):
        new_block = standard_block.copy()
        new_block[i] = '.'
        lib.append(format_block(new_block))

    # Two goals
    for i in range(4):
        for j in range(i, 4):
            new_block = standard_block.copy()
            new_block[i] = '.'
            new_block[j] = '.'
            lib.append(format_block(new_block))

    # Single wall and player
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '#'
            new_block[j] = '@'
            lib.append(format_block(new_block))

    # Two walls and player
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '#'
                new_block[j] = '#'
                new_block[k] = '@'
                lib.append(format_block(new_block))

    # Single wall and stone
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '#'
            new_block[j] = '$'
            lib.append(format_block(new_block))

    # Two walls and stone
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '#'
                new_block[j] = '#'
                new_block[k] = '$'
                lib.append(format_block(new_block))

    # Single wall and two stones
    # Don't have two stones directly adjacent
    lib.append(
        "$#\n"
        " $\n"
    )
    lib.append(
        "$ \n"
        "#$\n"
    )
    lib.append(
        "#$\n"
        "$ \n"
    )
    lib.append(
        " $\n"
        "$#\n"
    )

    # Two walls and two stones
    # Don't have two stones directly adjacent
    lib.append(
        "$#\n"
        "#$\n"
    )
    lib.append(
        "$#\n"
        "#$\n"
    )

    # Single wall and goal
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '#'
            new_block[j] = '.'
            lib.append(format_block(new_block))

    # Two walls and goal
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '#'
                new_block[j] = '#'
                new_block[k] = '.'
                lib.append(format_block(new_block))

    # Single wall and two goals
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '.'
                new_block[j] = '.'
                new_block[k] = '#'
                lib.append(format_block(new_block))

    # Two walls and two goals
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                for m in range(k, 4):
                    if k == i or k == j or m == i or m == j:
                        continue
                    new_block = standard_block.copy()
                    new_block[i] = '#'
                    new_block[j] = '#'
                    new_block[k] = '.'
                    new_block[m] = '.'
                    lib.append(format_block(new_block))

    # Single stone and player
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '$'
            new_block[j] = '@'
            lib.append(format_block(new_block))

    # Two stones and player
    # Don't have two stones directly adjacent
    lib.append(
        "$@\n"
        " $\n"
    )
    lib.append(
        "$ \n"
        "@$\n"
    )
    lib.append(
        "@$\n"
        "$ \n"
    )
    lib.append(
        " $\n"
        "$@\n"
    )

    # Single goal and player
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '.'
            new_block[j] = '@'
            lib.append(format_block(new_block))

    # Two goals and player
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '.'
                new_block[j] = '.'
                new_block[k] = '@'
                lib.append(format_block(new_block))

    # Single goal and stone
    for i in range(4):
        for j in range(4):
            if j == i:
                continue
            new_block = standard_block.copy()
            new_block[i] = '.'
            new_block[j] = '$'
            lib.append(format_block(new_block))

    # Two goals and stone
    for i in range(4):
        for j in range(i, 4):
            for k in range(1, 4):
                if k == i or k == j:
                    continue
                new_block = standard_block.copy()
                new_block[i] = '.'
                new_block[j] = '.'
                new_block[k] = '$'
                lib.append(format_block(new_block))

    # Single goal and two stones
    # Don't have two stones directly adjacent
    lib.append(
        "$.\n"
        " $\n"
    )
    lib.append(
        "$ \n"
        ".$\n"
    )
    lib.append(
        ".$\n"
        "$ \n"
    )
    lib.append(
        " $\n"
        "$.\n"
    )

    # Two goals and two stones
    # Don't have two stones directly adjacent
    lib.append(
        "$.\n"
        ".$\n"
    )
    lib.append(
        ".$\n"
        "$.\n"
    )

    return lib
