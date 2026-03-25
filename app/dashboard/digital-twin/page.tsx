'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useState } from 'react';
import { Play } from 'lucide-react';

const simulationResults = [
  { hour: 0, solar: 0, wind: 140, battery: 3000, demand: 800 },
  { hour: 4, solar: 0, wind: 160, battery: 2800, demand: 700 },
  { hour: 8, solar: 800, wind: 120, battery: 3200, demand: 1100 },
  { hour: 12, solar: 2200, wind: 90, battery: 4500, demand: 1300 },
  { hour: 16, solar: 1500, wind: 110, battery: 4200, demand: 1200 },
  { hour: 20, solar: 100, wind: 150, battery: 3500, demand: 1400 },
  { hour: 23, solar: 0, wind: 140, battery: 3000, demand: 900 },
];

export default function DigitalTwinPage() {
  const [simulationRun, setSimulationRun] = useState(false);
  const [params, setParams] = useState({
    solarCapacity: 3000,
    windCapacity: 2500,
    batteryCapacity: 5000,
    demandPeak: 1400,
  });

  const handleSimulation = () => {
    setSimulationRun(true);
    setTimeout(() => setSimulationRun(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Digital Twin Simulation</h2>
        <p className="text-muted-foreground">Test scenarios and optimize your energy system virtually</p>
      </div>

      {/* Simulation Parameters */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4">
        <CardHeader>
          <CardTitle className="text-foreground">Simulation Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Solar Capacity (kW)</label>
              <Input
                type="number"
                value={params.solarCapacity}
                onChange={(e) => setParams({ ...params, solarCapacity: Number(e.target.value) })}
                className="bg-input border-border text-foreground"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Wind Capacity (kW)</label>
              <Input
                type="number"
                value={params.windCapacity}
                onChange={(e) => setParams({ ...params, windCapacity: Number(e.target.value) })}
                className="bg-input border-border text-foreground"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Battery Capacity (kWh)</label>
              <Input
                type="number"
                value={params.batteryCapacity}
                onChange={(e) => setParams({ ...params, batteryCapacity: Number(e.target.value) })}
                className="bg-input border-border text-foreground"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Peak Demand (kW)</label>
              <Input
                type="number"
                value={params.demandPeak}
                onChange={(e) => setParams({ ...params, demandPeak: Number(e.target.value) })}
                className="bg-input border-border text-foreground"
              />
            </div>
          </div>

          <Button
            onClick={handleSimulation}
            className="mt-6 bg-primary text-primary-foreground hover:opacity-90 w-full md:w-auto"
            disabled={simulationRun}
          >
            <Play className="w-4 h-4 mr-2" />
            {simulationRun ? 'Running Simulation...' : 'Run Simulation'}
          </Button>
        </CardContent>
      </Card>

      {/* Simulation Results */}
      {simulationRun && (
        <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '100ms' }}>
          <CardHeader>
            <CardTitle className="text-foreground">Simulation In Progress...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-primary animate-pulse"></div>
                <p className="text-muted-foreground">Analyzing energy patterns with new parameters...</p>
              </div>
              <div className="w-full bg-muted/30 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-primary animate-pulse" style={{ width: '60%' }}></div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Energy Balance Chart */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '150ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground">24-Hour Energy Balance Simulation</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={simulationResults}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="hour" stroke="#ffffff60" />
              <YAxis stroke="#ffffff60" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #ffffff20', borderRadius: '8px' }}
                labelStyle={{ color: '#ffffff' }}
              />
              <Line type="monotone" dataKey="solar" stroke="#fbbf24" strokeWidth={2} dot={false} name="Solar Output" />
              <Line type="monotone" dataKey="wind" stroke="#3b82f6" strokeWidth={2} dot={false} name="Wind Output" />
              <Line type="monotone" dataKey="battery" stroke="#10b981" strokeWidth={2} dot={false} name="Battery Level" />
              <Line type="monotone" dataKey="demand" stroke="#ef4444" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Demand" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Self-Sufficiency', value: '82%', color: 'text-green-500', icon: '📊' },
          { label: 'Grid Independence', value: '78%', color: 'text-blue-500', icon: '🔌' },
          { label: 'Cost Savings', value: '£8,450/year', color: 'text-emerald-500', icon: '💰' },
          { label: 'CO₂ Reduction', value: '52 tonnes', color: 'text-yellow-500', icon: '🌱' },
        ].map((item, i) => (
          <Card key={i} className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: `${200 + i * 50}ms` }}>
            <CardContent className="pt-6">
              <p className="text-xs text-muted-foreground mb-2">{item.label}</p>
              <p className={`text-3xl font-bold ${item.color}`}>{item.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Utilization Chart */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '300ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground">System Utilization</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={simulationResults}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="hour" stroke="#ffffff60" />
              <YAxis stroke="#ffffff60" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #ffffff20', borderRadius: '8px' }}
                labelStyle={{ color: '#ffffff' }}
              />
              <Bar dataKey="solar" fill="#fbbf24" radius={[4, 4, 0, 0]} />
              <Bar dataKey="wind" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '350ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground">Simulation Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              'Increasing solar capacity to 3,500 kW would improve self-sufficiency by 8%',
              'Adding 1,000 kWh battery capacity would reduce grid imports by 15%',
              'Peak demand occurs at 8 PM - consider load shifting strategies',
              'Current system handles 94% of demand without grid import during peak solar hours',
            ].map((insight, i) => (
              <div key={i} className="flex gap-3 p-3 bg-muted/30 rounded-lg border border-border/50">
                <span className="text-primary font-bold flex-shrink-0">•</span>
                <p className="text-sm text-muted-foreground">{insight}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
