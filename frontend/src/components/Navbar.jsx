const links = ['Features', 'Pricing', 'Login'];

function Navbar() {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-4 lg:px-8">
        <a href="#" className="text-lg font-bold tracking-tight text-slate-900">
          TestGen AI
        </a>

        <div className="hidden items-center gap-8 md:flex">
          {links.map((link) => (
            <a
              key={link}
              href={`#${link.toLowerCase()}`}
              className="text-sm font-medium text-slate-600 transition hover:text-brand-700"
            >
              {link}
            </a>
          ))}
        </div>

        <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700">
          Get Started
        </button>
      </nav>
    </header>
  );
}

export default Navbar;
