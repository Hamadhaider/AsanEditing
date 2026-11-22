import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'AsanEditing — AI Documentary Studio', description: 'Your script in. A documentary out.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
