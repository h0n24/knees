import './globals.css';

export const metadata = {
  title: 'Knee Training Tracker',
  description: 'Daily knee training tracker with trainer oversight.'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
