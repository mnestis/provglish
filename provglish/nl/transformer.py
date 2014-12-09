from provglish import transform

import templates

transformer = transform.Transformer()
for template in templates.all_templates:
    transformer.register_template(template)
