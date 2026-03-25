'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import { TrendingUp, Calendar, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';

const consumptionByDevice = [
  { name: 'HVAC Systems', value: 35 },
  { name: 'Lighting', value: 22 },
  { name: 'Computing', value: 18 },
  { name: 'Equipment', value: 15 },
  { name: 'Other', value: 10 },
];

const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#6b7280'];

export default function AnalyticsPage() {

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
        Loading Analytics...
      </div>
    );
  }

  // ✅ create dynamic chart data
  const chartData = Array.from({ length: 7 }, (_, i) => ({
    time: `Day ${i + 1}`,
    solar: energyData.solar_prediction + Math.random() * 100,
    wind: energyData.wind_prediction + Math.random() * 50,
    grid: energyData.decision.grid_usage,
  }));

  // ✅ metrics
  const analyticsMetrics = [
    {
      label: 'Total Generation',
      value: (energyData.solar_prediction + energyData.wind_prediction).toFixed(2) + ' kW',
      change: '+Live',
      color: 'text-green-500',
    },
    {
      label: 'Solar Output',
      value: energyData.solar_prediction.toFixed(2) + ' kW',
      change: '+Active',
      color: 'text-yellow-500',
    },
    {
      label: 'Wind Output',
      value: energyData.wind_prediction.toFixed(2) + ' kW',
      change: '+Active',
      color: 'text-blue-500',
    },
    {
      label: 'Grid Usage',
      value: energyData.decision.grid_usage + ' kW',
      change: 'Dynamic',
      color: 'text-red-500',
    },
  ];

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-2">Analytics & Insights</h2>
          <p className="text-muted-foreground">AI-based energy insights</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Filter className="w-4 h-4" /> Filter</Button>
          <Button variant="outline"><Calendar className="w-4 h-4" /> Date</Button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {analyticsMetrics.map((m, i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle className="text-sm">{m.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{m.value}</div>
              <div className={`text-xs ${m.color}`}>
                <TrendingUp className="inline w-3 h-3" /> {m.change}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Line Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Energy Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line dataKey="solar" stroke="#fbbf24" />
                <Line dataKey="wind" stroke="#3b82f6" />
                <Line dataKey="grid" stroke="#ef4444" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Consumption</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={consumptionByDevice} dataKey="value">
                  {consumptionByDevice.map((_, i) => (
                    <Cell key={i} fill={colors[i]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Energy Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="solar" fill="#fbbf24" />
              <Bar dataKey="wind" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle>AI Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <p>System is currently <b>{energyData.decision.status}</b></p>
          <p>Battery Action: {energyData.decision.battery_action}</p>
          <p>Total Energy Used: {energyData.decision.energy_used}</p>
        </CardContent>
      </Card>

    </div>
  );
}