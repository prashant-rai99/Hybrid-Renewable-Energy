'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Leaf, TrendingUp, Zap } from 'lucide-react';

export default function CarbonAnalyticsPage() {

  const [energyData, setEnergyData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getEnergyData();
      setEnergyData(data);
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  // ✅ loading
  if (!energyData) {
    return (
      <div className="flex items-center justify-center h-screen text-white text-xl">
        Loading Carbon Data...
      </div>
    );
  }

  // ✅ simple carbon calculation (demo logic)
  const totalEnergy = energyData.solar_prediction + energyData.wind_prediction;
  const carbonSaved = (totalEnergy * 0.0007).toFixed(2); // approx factor
  const renewablePercent = ((totalEnergy / (totalEnergy + energyData.decision.grid_usage + 1)) * 100).toFixed(1);

  // ✅ chart data
  const carbonData = Array.from({ length: 7 }, (_, i) => ({
    date: `Day ${i + 1}`,
    carbon: parseFloat(carbonSaved) + Math.random(),
    renewable: parseFloat(renewablePercent),
  }));

  return (
    <div className="space-y-8">

      {/* Title */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Carbon Analytics</h2>
        <p className="text-muted-foreground">AI-based sustainability tracking</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm">CO₂ Avoided</p>
            <p className="text-3xl font-bold text-green-500">{carbonSaved} tonnes</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm">Renewable %</p>
            <p className="text-3xl font-bold text-yellow-500">{renewablePercent}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm">Grid Usage</p>
            <p className="text-3xl font-bold text-red-500">{energyData.decision.grid_usage} kW</p>
          </CardContent>
        </Card>

      </div>

      {/* Line Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Carbon vs Renewable</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={carbonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line dataKey="carbon" stroke="#ef4444" />
              <Line dataKey="renewable" stroke="#10b981" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Bar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>CO₂ Reduction Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={carbonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="carbon" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <p>System currently: <b>{energyData.decision.status}</b></p>
          <p>Battery: {energyData.decision.battery_action}</p>
          <p>Energy Used: {energyData.decision.energy_used}</p>
        </CardContent>
      </Card>

    </div>
  );
}