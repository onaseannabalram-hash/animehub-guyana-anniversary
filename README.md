# AnimeHub Guyana Anniversary Website

A single-page Flask web application built for AnimeHub Guyana’s anniversary celebration.  
The site combines anime-inspired design with functional order management, dual database storage, and responsive layouts for both mobile and desktop devices.

---

## ✨ Features

- **Anniversary Sale Packages**: Browse curated packages (Comic, Deluxe, Mystery) with descriptions and prices.
- **Place Orders**: Customers enter name, address, region, and package selection.
- **Shipping Calculation**: Shipping cost is automatically added based on region.
- **Order Success Page**: Displays confirmation details after submission.
- **Edit & Cancel Orders**: Orders can be updated or canceled, with changes reflected in both databases.
- **Dual Database Storage**:
  - **SQLite**: Primary transactional storage.
  - **MongoDB**: Mirrored database for live monitoring and analytics.
- **Corporate Information**: Store hours, company background, and contact details.
- **Social Media Integration**: Clickable icons allow users to send emails or view AnimeHub Guyana’s platforms directly.
- **Responsive Design**: Optimized for mobile devices and computers.

---

## 🖌️ Design Choices

- **Fonts**: Headings use *Bangers* font for bold, comic-inspired style.
- **Colors**: Adapted from the AnimeHub Guyana logo — pink (#ff3366) with glowing yellow highlights.
- **Glow Effects**: Text shadows and glowing buttons reinforce anime-inspired aesthetics.
- **Consistency**: Modular CSS ensures headings, buttons, and confirmation blocks share a unified look.

---

## ⚙️ Tech Stack

- **Front-End**: HTML, CSS, JavaScript, Bootstrap
- **Middleware**: Flask (Python)
- **Back-End**: SQLite (primary) + MongoDB (mirroring)
- **Tools**: MongoDB Compass for live data visualization

---

## 🚀 Launch Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/animehub-guyana-anniversary.git
   cd animehub-guyana-anniversary
