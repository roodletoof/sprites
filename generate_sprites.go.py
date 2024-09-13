import os
import re

go_file_template = '''\
package sprites

import (
    "embed"
    "github.com/hajimehoshi/ebiten/v2"
    _ "image/png"
    "image"
    "bytes"
)

//go:embed assets/*
var embeddedAssets embed.FS

{variables}

func init() {{
{init_code}
}}

func loadImage(path string) *ebiten.Image {{
    file, err := embeddedAssets.ReadFile(path)
    if err != nil {{
        log.Fatalf("failed to load image: %s, error: %v", path, err)
    }}

    img, err := png.Decode(bytes.NewReader(file))
    if err != nil {{
        log.Fatalf("failed to decode image: %s, error: %v", path, err)
    }}

    return ebiten.NewImageFromImage(img)
}}
'''

def camel_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def generate_go_code(assets_dir):
    variables = []
    init_code = []

    for root, _, files in os.walk(assets_dir):
        for file in files:
            if file.endswith(".png"):
                relative_path = os.path.relpath(os.path.join(root, file), assets_dir)
                var_name = re.sub(r'\W+', '', camel_case(relative_path))
                var_declaration = f"var {var_name} *ebiten.Image"
                init_line = f"{var_name} = loadImage(\"assets/{relative_path}\")"

                variables.append(var_declaration)
                init_code.append(init_line)

    go_code = go_file_template.format(
        variables='\n'.join(variables),
        init_code='\n    '.join(init_code)
    )

    return go_code

assets_dir = 'assets'  # Path to your assets directory
output_file = 'assets.go'

# Generate the Go file
go_code = generate_go_code(assets_dir)

# Write to file
with open(output_file, 'w') as f:
    f.write(go_code)

print(f"Go file generated: {output_file}")
