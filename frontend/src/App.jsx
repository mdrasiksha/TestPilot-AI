import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Pricing from './components/Pricing';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-50/40 via-white to-slate-50">
      <Navbar />
      <main>
        <Hero />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}

export default App;
