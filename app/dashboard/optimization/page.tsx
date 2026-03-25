'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Zap, Clock, TrendingUp } from 'lucide-react';

export default function OptimizationPage() {

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

  if (!energyData) {
    return <div className="text-center mt-20 text-xl">Loading Optimization...</div>;
  }

  // ✅ dynamic recommendations
  const recommendations = [
    {
      id: 1,
      type: 'charge',
      title: 'Charge Battery',
      time: 'Now',
      reason: 'Solar production high',
      savings: 'Maximize storage',
    },
    {
      id: 2,
      type: 'use',
      title: 'Use Solar Power',
      time: 'Next 2 hrs',
      reason: 'Avoid grid usage',
      savings: 'Save energy cost',
    },
    {
      id: 3,
      type: 'discharge',
      title: 'Discharge Battery',
      time: 'Evening',
      reason: 'Demand high, solar low',
      savings: 'Reduce grid dependency',
    },
  ];

  // charts (same as before)
  const optimizationData = [
    { time: '12 AM', savings: 0 },
    { time: '4 AM', savings: 150 },
    { time: '8 AM', savings: 320 },
    { time: '12 PM', savings: 520 },
    { time: '4 PM', savings: 680 },
    { time: '8 PM', savings: 450 },
  ];

  const scheduleData = [
    { hour: '0', solar: 0, demand: 800 },
    { hour: '6', solar: 100, demand: 850 },
    { hour: '9', solar: energyData.solar_prediction, demand: 1200 },
    { hour: '12', solar: energyData.solar_prediction * 1.5, demand: 1300 },
    { hour: '15', solar: energyData.solar_prediction, demand: 1100 },
    { hour: '18', solar: 200, demand: 1400 },
    { hour: '21', solar: 0, demand: 1100 },
  ];

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Energy Optimization</h2>
        <p className="text-muted-foreground">AI recommendations for efficiency</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6 flex justify-between">
            <div>
              <p className="text-sm">Savings</p>
              <p className="text-2xl font-bold text-green-500">
                {(energyData.solar_prediction * 0.05).toFixed(2)} ₹
              </p>
            </div>
            <TrendingUp />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 flex justify-between">
            <div>
              <p className="text-sm">CO₂ Saved</p>
              <p className="text-2xl font-bold text-blue-500">
                {(energyData.solar_prediction * 0.02).toFixed(2)} kg
              </p>
            </div>
            <Zap />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 flex justify-between">
            <div>
              <p className="text-sm">Efficiency</p>
              <p className="text-2xl font-bold text-purple-500">92%</p>
            </div>
            <ArrowUp />
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {recommendations.map((rec) => (
            <div key={rec.id} className="p-3 border rounded flex justify-between">
              <div>
                <p className="font-semibold">{rec.title}</p>
                <p className="text-xs text-gray-400">{rec.reason}</p>
              </div>
              <Button size="sm">Apply</Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Savings Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Daily Savings</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={optimizationData}>
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="savings" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Schedule */}
      <Card>
        <CardHeader>
          <CardTitle className="flex gap-2 items-center">
            <Clock /> Schedule
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scheduleData}>
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line dataKey="solar" stroke="#fbbf24" />
              <Line dataKey="demand" stroke="#ef4444" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

    </div>
  );
}