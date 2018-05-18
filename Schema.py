schema = {
    "type": "object",
    "properties": {
        "Figures": {
            "type": "array",
            "items": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["point"]},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "color": {"type": "string"}
                        },
                        "required": ["type", "x", "y"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["rectangle"]},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"},
                            "color": {"type": "string"}
                        },
                        "required": ["type", "x", "y", "width", "height"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["square"]},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "size": {"type": "integer"},
                            "color": {"type": "string"}
                        },
                        "required": ["type", "x", "y", "size"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["circle"]},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "radius": {"type": "integer"},
                            "color": {"type": "string"}
                        },
                        "required": ["type", "x", "y", "radius"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["polygon"]},
                            "points": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "items": {"type": "integer"}
                                }
                            },
                            "color": {"type": "string"}
                        },
                        "required": ["type", "points"]
                    },
                ],
            }
        },
        "Screen": {
            "type": "object",
            "properties": {
                "width": {"type": "integer", "minimum": 1},
                "height": {"type": "integer", "minimum": 1},
                "bg_color": {"type": "string"},
                "fg_color": {"type": "string"}
            }
        },
        "Palette": {
            "type": "object"
        }
    }
}
