def draw_connector(slide, shape_spec, id_map):
    style = shape_spec.get("style", {})
    from_id = shape_spec["from"]
    to_id = shape_spec["to"]
    from_shape = id_map[from_id]
    to_shape = id_map[to_id]

    fx = from_shape.left + from_shape.width // 2
    fy = from_shape.top + from_shape.height // 2
    tx = to_shape.left + to_shape.width // 2
    ty = to_shape.top + to_shape.height // 2

    curve = style.get("curve", False)
    color = hex_to_rgb(style.get("color", "#555555"))
    width = Pt(style.get("width", 2))

    if curve:
        # --- compute midpoints for a smooth S-curve ---
        mx1 = fx + (tx - fx) * 0.33
        my1 = fy - (abs(tx - fx) * 0.25)

        mx2 = fx + (tx - fx) * 0.66
        my2 = ty + (abs(tx - fx) * 0.25)

        # segment 1
        c1 = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, fx, fy, int(mx1), int(my1)
        )
        c1.line.color.rgb = color
        c1.line.width = width

        # segment 2
        c2 = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, int(mx1), int(my1), int(mx2), int(my2)
        )
        c2.line.color.rgb = color
        c2.line.width = width

        # segment 3
        c3 = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, int(mx2), int(my2), tx, ty
        )
        c3.line.color.rgb = color
        c3.line.width = width

    else:
        # straight connector
        conn = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, fx, fy, tx, ty
        )
        conn.line.color.rgb = color
        conn.line.width = width
