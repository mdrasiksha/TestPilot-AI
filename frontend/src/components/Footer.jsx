function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-5 py-8 text-sm text-slate-600 md:flex-row lg:px-8">
        <p>© {new Date().getFullYear()} TestGen AI</p>
        <div className="flex items-center gap-6">
          <a href="#features" className="transition hover:text-brand-700">
            Features
          </a>
          <a href="#pricing" className="transition hover:text-brand-700">
            Pricing
          </a>
          <a href="#" className="transition hover:text-brand-700">
            Login
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
