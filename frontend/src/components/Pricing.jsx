const plans = [
  {
    name: 'Free',
    price: '$0',
    description: 'Perfect for individual testers exploring AI-generated test cases.',
    features: ['Up to 20 test cases/month', 'Basic templates', 'Community support'],
    cta: 'Start Free',
    featured: false,
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'Best for QA professionals shipping faster with confident coverage.',
    features: ['Unlimited test generation', 'Advanced scenario coverage', 'Export to Jira & CSV'],
    cta: 'Choose Pro',
    featured: true,
  },
  {
    name: 'Team',
    price: '$99',
    description: 'Collaborate across QA teams with shared workflows and governance.',
    features: ['Shared workspace', 'Role-based access', 'Priority support'],
    cta: 'Contact Sales',
    featured: false,
  },
];

function Pricing() {
  return (
    <section id="pricing" className="mx-auto w-full max-w-6xl px-5 py-16 lg:px-8 lg:py-24">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Simple, transparent pricing</h2>
        <p className="mt-4 text-slate-600">Choose a plan that fits your QA velocity and team size.</p>
      </div>

      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <article
            key={plan.name}
            className={`rounded-2xl border bg-white p-7 shadow-soft ${
              plan.featured ? 'border-brand-600 ring-2 ring-brand-100' : 'border-slate-200'
            }`}
          >
            {plan.featured && (
              <span className="mb-4 inline-flex rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
                Most Popular
              </span>
            )}
            <h3 className="text-xl font-semibold text-slate-900">{plan.name}</h3>
            <p className="mt-2 text-4xl font-bold tracking-tight text-slate-900">
              {plan.price}
              <span className="text-base font-medium text-slate-500">/mo</span>
            </p>
            <p className="mt-4 text-sm leading-relaxed text-slate-600">{plan.description}</p>

            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-brand-600" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            <button
              className={`mt-8 w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition ${
                plan.featured
                  ? 'bg-brand-600 text-white hover:bg-brand-700'
                  : 'border border-slate-300 bg-white text-slate-700 hover:border-brand-200 hover:text-brand-700'
              }`}
            >
              {plan.cta}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Pricing;
