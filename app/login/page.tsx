'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Mock authentication - simulate delay
    setTimeout(() => {
      router.push('/dashboard');
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-in fade-in duration-500">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-lg bg-primary flex items-center justify-center mx-auto mb-4">
            <span className="text-primary-foreground text-xl font-bold">⚡</span>
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">EnergyOS</h1>
          <p className="text-muted-foreground">Intelligent Energy Management</p>
        </div>

        {/* Login Form */}
        <div className="bg-card border border-border rounded-lg p-6 space-y-6">
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Email Address</label>
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-input border-border text-foreground"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-input border-border text-foreground"
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary text-primary-foreground hover:opacity-90"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-muted-foreground">Or continue as demo</span>
            </div>
          </div>

          {/* Demo button */}
          <Button
            type="button"
            variant="outline"
            className="w-full border-border text-foreground hover:bg-muted"
            onClick={() => {
              setEmail('demo@energyos.com');
              setPassword('demo123');
              setTimeout(() => router.push('/dashboard'), 300);
            }}
          >
            Enter as Demo User
          </Button>

          {/* Signup link */}
          <div className="text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <Link href="/signup" className="text-primary hover:underline font-medium">
              Sign up here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
