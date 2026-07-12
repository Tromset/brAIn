# site.md — the Madame Martin website

> 🧠 [Hub](README.md) · [Variables](brain.yaml) · Requirements: [notes.md](notes.md) · Tasks: [todo.md](todo.md)

One static page, pure HTML/CSS (decision logged in [notes.md](notes.md)). The greeting "Salut à tous, c'est Madame Martin" is imposed by the client — do not reword it.

## HTML — `index.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Madame Martin — Pâtisserie maison</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <h1>Salut à tous</h1>
    <p>C'est Madame Martin — pâtisserie maison à Lyon depuis 1998.</p>
    <a class="btn" href="#commander">Commander un gâteau</a>
  </header>

  <main>
    <section id="apropos">
      <h2>À propos</h2>
      <p>Tartes, éclairs et gâteaux d'anniversaire faits main, avec des
      ingrédients du marché Saint-Antoine. Tout est préparé le matin même.</p>
    </section>

    <section id="specialites">
      <h2>Spécialités</h2>
      <ul>
        <li>Tarte pralinée lyonnaise — 24 €</li>
        <li>Éclair café — 4,50 €</li>
        <li>Gâteau d'anniversaire sur mesure — à partir de 35 €</li>
      </ul>
    </section>

    <section id="commander">
      <h2>Commander</h2>
      <p>Par téléphone au 04 72 00 00 00 ou par email :
      <a href="mailto:contact@madame-martin.example">contact@madame-martin.example</a>.
      Commandes 48&nbsp;h à l'avance.</p>
    </section>
  </main>

  <footer>
    <p>© 2026 Madame Martin — 12 rue des Capucins, 69001 Lyon</p>
  </footer>
</body>
</html>
```

## CSS — `style.css`

The pink `#d96c8a` was color-picked from the client's cake-box logo ([notes.md](notes.md)).

```css
:root {
  --rose: #d96c8a;
  --creme: #fdf6ee;
  --encre: #3a2e2a;
}

* { box-sizing: border-box; margin: 0; }

body {
  font-family: Georgia, "Times New Roman", serif;
  background: var(--creme);
  color: var(--encre);
  line-height: 1.6;
}

.hero {
  background: var(--rose);
  color: white;
  text-align: center;
  padding: 4rem 1rem;
}

.hero h1 { font-size: 2.5rem; }

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.6rem 1.4rem;
  background: white;
  color: var(--rose);
  border-radius: 999px;
  text-decoration: none;
  font-weight: bold;
}

main {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

section { margin-bottom: 2rem; }

h2 {
  color: var(--rose);
  border-bottom: 2px solid var(--rose);
  padding-bottom: 0.25rem;
}

footer {
  text-align: center;
  font-size: 0.85rem;
  padding: 1.5rem;
  color: #8a7a72;
}
```
