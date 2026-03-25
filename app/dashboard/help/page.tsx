'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, MessageCircle, Mail, Phone, FileText, Search, Book, Lightbulb, Settings, TrendingUp, Zap, AlertCircle, ArrowRight } from 'lucide-react';
import { useState } from 'react';

const faqs = [
  {
    category: 'Getting Started',
    question: 'How do I get started with EnergyOS?',
    answer: 'Start by logging in to your account. The Dashboard page provides an overview of your entire energy system. Explore the Monitoring page to see real-time metrics, then check Settings to configure alerts and thresholds. Our onboarding guide in the Help section walks you through each feature step-by-step.',
  },
  {
    category: 'Energy Monitoring',
    question: 'What does the real-time monitoring show?',
    answer: 'Real-time monitoring displays current generation from solar panels and wind turbines, battery charge level (%), grid import/export status, and system efficiency. Gauges show power flow distribution, and the system health indicator alerts you to any issues. Data updates every few seconds for live visibility.',
  },
  {
    category: 'Forecasting',
    question: 'How does the energy forecasting work?',
    answer: 'Our AI-powered forecasting uses historical weather patterns, current conditions, and ML models to predict generation for 24 hours and 7 days with 94% accuracy. Solar forecasts account for cloud cover and seasonal patterns. Wind forecasts use atmospheric pressure and wind speed data. The system learns continuously from actual vs. predicted data.',
  },
  {
    category: 'Optimization',
    question: 'How can I optimize my energy usage?',
    answer: 'Visit the Optimization page to view personalized AI recommendations. The system analyzes weather forecasts, electricity rates, demand patterns, and battery state to suggest optimal battery charging/discharging times, load scheduling, and excess energy export opportunities. Implement recommendations with one click.',
  },
  {
    category: 'Digital Twin',
    question: 'What is the Digital Twin simulation used for?',
    answer: 'The Digital Twin lets you test capacity scenarios without physical changes. Simulate adding solar panels, wind turbines, or battery storage and see projected impact on self-sufficiency, costs, and ROI. Test multiple scenarios to find the optimal configuration before making actual investments.',
  },
  {
    category: 'Analytics',
    question: 'What analytics are available?',
    answer: 'Analytics include energy consumption breakdown by source (solar, wind, grid, battery), hourly/daily/monthly trends, peak usage times, system efficiency metrics, and cost analysis. Charts show renewable vs. grid energy, battery cycling patterns, and seasonal variations. Export data for further analysis.',
  },
  {
    category: 'Carbon Tracking',
    question: 'What is the carbon impact calculation based on?',
    answer: 'Carbon savings are calculated from your region\'s grid energy mix and renewable generation. We use official carbon intensity factors from grid operators. Each kWh of renewable energy offsets equivalent grid electricity\'s carbon footprint. View monthly carbon offset equivalent (trees planted, cars taken off road).',
  },
  {
    category: 'Reports',
    question: 'Can I export my data and generate reports?',
    answer: 'Yes! From the Reports page, generate custom reports in PDF, Excel, or CSV formats. Choose time periods (monthly, quarterly, annual) and report types: energy summaries, performance analysis, carbon impact, financial analysis, or custom combinations. Schedule automated reports sent to your email.',
  },
  {
    category: 'Settings',
    question: 'How do I configure alerts and notifications?',
    answer: 'Go to Settings > Alerts & Notifications. Set thresholds for: battery level alerts, grid import alerts, system efficiency alerts, and temperature warnings. Choose notification methods (email, in-app, SMS). Subscribe to daily, weekly, or monthly summary reports. View alert history and manage notification preferences.',
  },
  {
    category: 'Technical',
    question: 'What are the system requirements?',
    answer: 'EnergyOS works on modern browsers: Chrome/Edge v90+, Firefox v88+, Safari v14+, and mobile browsers. Recommended: 8GB RAM, stable internet (2+ Mbps), and screen resolution 1024x768 or larger for optimal experience. Works on desktop, tablet, and mobile devices.',
  },
];

const helpTopics = [
  {
    title: 'Getting Started',
    description: 'Complete guide to navigating the dashboard and understanding your energy system',
    icon: Book,
    color: 'from-blue-500/20 to-blue-600/20',
  },
  {
    title: 'Real-time Monitoring',
    description: 'Understanding gauges, power flow, and system health indicators',
    icon: Zap,
    color: 'from-yellow-500/20 to-yellow-600/20',
  },
  {
    title: 'Energy Forecasting',
    description: 'How AI predictions work and how to use forecasts for planning',
    icon: TrendingUp,
    color: 'from-green-500/20 to-green-600/20',
  },
  {
    title: 'Optimization Tips',
    description: 'Best practices for maximizing efficiency and cost savings',
    icon: Lightbulb,
    color: 'from-purple-500/20 to-purple-600/20',
  },
  {
    title: 'Alerts & Notifications',
    description: 'Setting up alerts, configuring thresholds, and managing preferences',
    icon: AlertCircle,
    color: 'from-red-500/20 to-red-600/20',
  },
  {
    title: 'System Settings',
    description: 'Configure preferences, integrations, and system behavior',
    icon: Settings,
    color: 'from-indigo-500/20 to-indigo-600/20',
  },
];

export default function HelpPage() {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(0);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFaqs = faqs.filter(faq =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-in fade-in slide-in-from-top-4 duration-500">
        <h1 className="text-4xl font-bold text-foreground mb-2">Help & Support</h1>
        <p className="text-lg text-muted-foreground">Find answers, learn features, and get support with EnergyOS</p>
      </div>

      {/* Search Bar */}
      <div className="relative animate-in fade-in slide-in-from-top-4 duration-500" style={{ animationDelay: '100ms' }}>
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search FAQs and documentation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-card border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Quick Support Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: MessageCircle, label: 'Live Chat', description: 'Chat with support team', time: 'Avg response: 5 min' },
          { icon: Mail, label: 'Email Support', description: 'support@energyos.com', time: 'Response: 24 hours' },
          { icon: Phone, label: 'Phone Support', description: '+1 (555) 123-4567', time: '9 AM - 6 PM EST' },
        ].map((support, i) => {
          const Icon = support.icon;
          return (
            <Card
              key={i}
              className="bg-card border-border hover:border-primary/50 hover:shadow-lg transition-all duration-300 animate-in fade-in slide-in-from-bottom-4"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <Icon className="w-8 h-8 text-primary" />
                  <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <h4 className="font-semibold text-foreground mb-1">{support.label}</h4>
                <p className="text-sm text-muted-foreground mb-2">{support.description}</p>
                <p className="text-xs text-primary/70 mb-4">{support.time}</p>
                <Button size="sm" className="w-full bg-primary text-primary-foreground hover:opacity-90">
                  Contact
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Help Topics */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '300ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground text-2xl">Browse Topics</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Select a topic to learn more</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {helpTopics.map((topic, i) => {
              const Icon = topic.icon;
              return (
                <button
                  key={i}
                  className={`relative overflow-hidden rounded-lg border border-border p-5 text-left transition-all duration-300 hover:border-primary hover:shadow-lg group bg-gradient-to-br ${topic.color}`}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-3">
                      <Icon className="w-6 h-6 text-primary" />
                      <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="font-semibold text-foreground text-sm mb-2">{topic.title}</h3>
                    <p className="text-xs text-muted-foreground">{topic.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* FAQ Section */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '400ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground text-2xl">Frequently Asked Questions</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">{filteredFaqs.length} questions found</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {filteredFaqs.length > 0 ? (
              filteredFaqs.map((faq, i) => (
                <div
                  key={i}
                  className="border border-border/50 rounded-lg overflow-hidden hover:border-primary/50 transition-all duration-300 hover:shadow-sm"
                >
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                    className="w-full flex items-start justify-between p-4 hover:bg-muted/30 transition-colors text-left"
                  >
                    <div className="flex-1">
                      <div className="text-xs font-semibold text-primary/70 uppercase tracking-wide mb-1">
                        {faq.category}
                      </div>
                      <span className="font-medium text-foreground">{faq.question}</span>
                    </div>
                    <ChevronDown
                      className={`w-5 h-5 text-muted-foreground flex-shrink-0 transition-transform duration-300 ${
                        expandedFaq === i ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  {expandedFaq === i && (
                    <div className="px-4 py-4 bg-muted/20 border-t border-border/50 animate-in fade-in slide-in-from-top-2 duration-300">
                      <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No questions found matching your search.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Documentation Links */}
      <Card className="bg-card border-border animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '500ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground flex items-center gap-2 text-2xl">
            <FileText className="w-6 h-6" />
            Documentation & Resources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'User Guide', description: 'Complete feature guide and walkthrough', badge: 'PDF', icon: '📖' },
              { title: 'API Documentation', description: 'Technical docs for developers and integrations', badge: 'Web', icon: '💻' },
              { title: 'Troubleshooting', description: 'Common issues and solutions', badge: 'Web', icon: '🔧' },
              { title: 'Getting Started', description: 'Step-by-step setup guide', badge: 'PDF', icon: '🚀' },
            ].map((doc, i) => (
              <div
                key={i}
                className="flex items-start gap-4 p-4 bg-muted/20 border border-border/50 rounded-lg hover:border-primary/50 hover:bg-muted/30 transition-all duration-300 cursor-pointer group"
              >
                <span className="text-2xl flex-shrink-0">{doc.icon}</span>
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground mb-1">{doc.title}</h4>
                  <p className="text-sm text-muted-foreground">{doc.description}</p>
                  <div className="mt-3 flex items-center gap-2">
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded font-medium">{doc.badge}</span>
                    <span className="text-xs text-primary opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                      Learn more <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* CTA Section */}
      <Card className="bg-gradient-to-r from-primary/15 to-secondary/15 border-primary/20 animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: '600ms' }}>
        <CardHeader>
          <CardTitle className="text-foreground text-2xl">Still have questions?</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-6">Our support team is here to help. Reach out anytime through chat, email, or phone.</p>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button className="bg-primary text-primary-foreground hover:opacity-90 flex-1">
              Start Live Chat
            </Button>
            <Button variant="outline" className="border-border text-foreground hover:bg-muted flex-1">
              Email Us
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
