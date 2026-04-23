function Hero() {
  return (
    <section id="features" className="mx-auto flex w-full max-w-6xl flex-col px-5 pb-16 pt-16 text-center lg:px-8 lg:pt-24">
      <p className="mx-auto mb-6 inline-flex rounded-full border border-brand-100 bg-brand-50 px-4 py-1 text-sm font-medium text-brand-700">
        Built for QA Teams and SDETs
      </p>
      <h1 className="mx-auto max-w-4xl text-balance text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
        Generate QA Test Cases in Seconds
      </h1>
      <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-600">
        AI-powered test case generation for testers and SDETs
      </p>

      <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <button className="w-full rounded-lg bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 sm:w-auto">
          Try for Free
        </button>
        <a
          href="#pricing"
          className="w-full rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-200 hover:text-brand-700 sm:w-auto"
        >
          View Pricing
        </a>
      </div>
    </section>
  );
}

export default Hero;
