# Pagina Web 2.0

## Instalación de dependencias

- Python (Flask):
  ```bash
  pip install flask
  ```
- Node.js (Tailwind CSS, PostCSS, Font Awesome):
  ```bash
  npm install -D tailwindcss postcss
  npm install --save @fortawesome/fontawesome-free
  npm install -g tailwindcss
  ```

## Estructura recomendada
- static/
  - css/
  - icons/
  - img/
  - js/
- templates/
- app.py
- ...

## Uso de Tailwind CSS
Puedes compilar los estilos con:
```bash
tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

## Uso de Font Awesome
Incluye en tu HTML:
```html
<link rel="stylesheet" href="/node_modules/@fortawesome/fontawesome-free/css/all.min.css">
``` 