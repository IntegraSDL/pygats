def color_generator():
    rgb = []
    for r in range(256):
        for g in range(256):
            for b in range(256):
                color = f"#{r:02x}{g:02x}{b:02x}"
                rgb.append(color)
                if len(rgb) >= 2000:
                     return rgb
    return rgb