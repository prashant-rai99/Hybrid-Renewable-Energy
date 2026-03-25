'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { TrendingUp, Zap, Wind, Battery } from 'lucide-react';

const dashboardData = [
  { time: '12 AM', consumption: 2400, generation: 2210 },
  { time: '4 AM', consumption: 1398, generation: 2290 },
  { time: '8 AM', consumption: 9800, generation: 2000 },
  { time: '12 PM', consumption: 3908, generation: 2181 },
  { time: '4 PM', consumption: 4800, generation: 2500 },
  { time: '8 PM', consumption: 3800, generation: 2100 },
];

const energyMix = [
  { name: 'Solar', value: 45 },
  { name: 'Wind', value: 30 },
  { name: 'Grid', value: 25 },
];

const COLORS = ['#22c55e', '#0ea5e9', '#f59e0b'];

export default function DashboardPage() {
  const [energyData, setEnergyData] = useState<any>(null);

  // ✅ LIVE API CALL
  useEffect(() => {
    const fetchData = async () => {
      const data = await getEnergyData();
      setEnergyData(data);
    };

    fetchData(); // first call

    const interval = setInterval(fetchData, 5000); // every 5 sec

    return () => clearInterval(interval);
  }, []);

  // ✅ LOADING SCREEN
  if (!energyData) {
    return (
      <div className="flex items-center justify-center h-screen text-white text-xl">
        Loading AI Data...
      </div>
    );
  }

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">Real-time AI Energy Monitoring</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        {/* Consumption */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Consumption</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {energyData.decision.energy_used} kW
            </p>
          </CardContent>
        </Card>

        {/* Generation */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Generation</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-500">
              {(energyData.solar_prediction + energyData.wind_prediction).toFixed(2)} kW
            </p>
          </CardContent>
        </Card>

        {/* Wind */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Wind Output</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-500">
              {energyData.wind_prediction.toFixed(2)}
            </p>
          </CardContent>
        </Card>

        {/* Battery */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Battery</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-bold">
              {energyData.decision.battery_action}
            </p>
          </CardContent>
        </Card>

      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Energy Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboardData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="consumption" stroke="#0ea5e9" />
                <Line type="monotone" dataKey="generation" stroke="#22c55e" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Energy Mix</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={energyMix} dataKey="value" innerRadius={60} outerRadius={100}>
                  {energyMix.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}