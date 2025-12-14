import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Bright, calm daily knee training</p>
        <h1>Knee Training Tracker</h1>
        <p className="lede">
          A Django + Next.js starter that keeps daily routines simple and gives trainers clear oversight.
        </p>
        <div className="actions">
          <Link className="button" href="/user/today">Start as user</Link>
          <Link className="button secondary" href="/trainer/dashboard">Trainer dashboard</Link>
        </div>
      </section>
    </main>
  );
}
