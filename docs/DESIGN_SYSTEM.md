# SkillBridge design system

The visual system uses midnight navy `#0B1026`, deep indigo `#181342`, electric violet `#6D28D9`, royal indigo `#4338CA`, lavender `#A78BFA`, sky `#38BDF8`, mint `#2DD4BF`, pearl `#F4F5FA`, and text `#0F172A`. Use `#475569` for small secondary text on light surfaces.

Inter is the body face and Plus Jakarta Sans the heading face; licensed local WOFF2 files have system fallbacks. Shared templates include the hero scene, banner, score ring, opportunity and stat cards. Internships use violet, research blue, and academic projects teal.

Keep forms, links and score values usable without JavaScript. Motion should be subtle, avoid delaying content, and respect `prefers-reduced-motion`. Do not invent scores or statistics. Preserve visible focus, labels, keyboard access, and 44px interaction targets.

The Tailwind input imports the existing style layers along with `tokens.css`, `components.css` and page-specific layers into the single compiled stylesheet. Consolidating the inherited legacy layers further remains a maintenance task.

The profile workspace groups editable portfolio sections, completeness and private resume management. The application form uses a labelled note field and explicit resume choices; a segmented match bar explains earned and available score points using the existing matching engine. Preserve native form controls and server-side validation as the fallback.
