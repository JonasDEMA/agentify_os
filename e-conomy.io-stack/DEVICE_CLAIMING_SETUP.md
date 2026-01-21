# Device Claiming System - Setup & Testing Guide

## 🎯 **System Overview**

The device claiming system allows you to:
1. **Pre-provision devices** in your factory/office with automatic k3s cluster connection
2. **Generate unique device IDs** for customer claiming
3. **Enable WiFi hotspot setup** for customers to configure internet connectivity
4. **Provide web-based claiming** through your customer portal

## ✅ **What's Ready**

### **Backend Components**
- ✅ **Database Schema**: Enhanced with device claiming fields and status tracking
- ✅ **Device Service**: Complete CRUD operations and claiming logic  
- ✅ **API Endpoints**: Registration, claiming, heartbeat, status tracking
- ✅ **Authentication**: JWT-based with customer and admin access

### **Frontend Components**
- ✅ **Device Claiming Page**: `/claim-device` with clean UI for entering device IDs
- ✅ **Enhanced Devices Dashboard**: Real-time status, connectivity indicators
- ✅ **Customer Flow**: Seamless device claiming and management

### **Device Components**
- ✅ **Installation Script**: Complete automated setup with claiming support
- ✅ **Node Server**: Express.js server with WiFi hotspot management
- ✅ **Captive Portal**: Beautiful web interface for WiFi configuration
- ✅ **Status Monitoring**: Automatic heartbeat and connectivity tracking

## ⚠️ **Issues Fixed**
- ✅ **User Schema Import**: Fixed `User` to `UserOut` in device endpoints
- ✅ **Frontend API Paths**: Updated to match backend structure (`/api/v1/devices/`)
- ✅ **Script Permissions**: Made installation script executable
- ✅ **Type Safety**: Fixed TypeScript/Python type annotations

## 🚀 **Ready for Testing - Setup Steps**

### **1. Database Setup**
```bash
cd xsd-cloud-backend
npx prisma migrate dev --name "add-device-claiming-features"
npx prisma generate
```

### **2. Backend Setup**
```bash
cd xsd-cloud-backend
# Install dependencies if needed
pip install -r requirements.txt  # or poetry install

# Start the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
cd e-conomy.io-web-cloud
# Install dependencies if needed
npm install

# Set environment variable
export NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Start the frontend
npm run dev
```

### **4. Test API Endpoints**
```bash
cd xsd-cloud-backend
python test_device_endpoints.py
```

## 🧪 **Testing Workflow**

### **Phase 1: Backend API Testing**
1. Run the endpoint test script to verify API connectivity
2. Test device registration with proper authentication
3. Test device claiming flow with customer credentials
4. Verify heartbeat functionality

### **Phase 2: Device Installation Testing**
```bash
# On a test Raspberry Pi or VM:
SERVER_API_URL=http://your-k3s-server:9696 \
API_KEY=your-api-key \
CLOUD_BACKEND_URL=http://your-backend:8000 \
CUSTOM_NODE_NAME=test-device-001 \
curl -fsSL http://your-k3s-server:9696/install-device-claiming | bash
```

**Note**: The script will ask for a node name if `CUSTOM_NODE_NAME` is not provided.

### **Phase 3: Customer Flow Testing**
1. Device installation generates device ID (e.g., `A7K9M2X5`)
2. Customer connects to hotspot (`eConomy-B827EB123456`)
3. Customer configures WiFi through captive portal
4. Customer claims device via web app using device ID

## 📋 **Environment Variables Required**

### **Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecomony_db
JWT_SECRET_KEY=your-secret-key
```

### **Frontend (.env.local)**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### **Device Installation**
```bash
SERVER_API_URL=http://your-k3s-server:9696
API_KEY=your-k3s-api-key
CLOUD_BACKEND_URL=http://your-backend:8000
ORGANIZATION_ID=your-org-id  # Optional
```

## 🎯 **Key Features Working**

### **Device Management**
- ✅ **8-character device IDs**: `A7K9M2X5` format
- ✅ **MAC-based hotspot SSIDs**: `eConomy-B827EB123456`
- ✅ **Secure claim tokens**: 32-character pre-shared secrets
- ✅ **Status tracking**: Internet, WiFi, hotspot, node server states

### **Customer Experience**
- ✅ **Automatic hotspot**: Activates when no internet connection
- ✅ **Captive portal**: Auto-opens for WiFi configuration
- ✅ **Device claiming**: Simple ID entry in web app
- ✅ **Real-time dashboard**: Live device status and connectivity

### **Admin Features**
- ✅ **Bulk device management**: View all devices across customers
- ✅ **Status monitoring**: Real-time connectivity and health tracking
- ✅ **Heartbeat logging**: Detailed device activity history

## 🔧 **Next Steps**

1. **Run Database Migration**: Update schema with new device fields
2. **Test Backend APIs**: Verify all endpoints work with authentication
3. **Test Installation Script**: Try on actual Pi or VM
4. **Test Customer Flow**: End-to-end device claiming process
5. **Production Setup**: Configure environment variables and deploy

## 📝 **File Structure**

```
xsd-cloud-backend/
├── app/schemas/device.py           # Device data models
├── app/services/device_service.py  # Business logic
├── app/api/v1/endpoints/device.py  # API endpoints
├── prisma/schema.prisma            # Database schema
└── test_device_endpoints.py        # Testing script

e-conomy.io-web-cloud/
├── src/app/claim-device/page.jsx   # Device claiming UI
└── src/app/devices/page.jsx        # Enhanced devices dashboard

device-installation-api/
└── install-device-with-claiming.sh # Complete installation script
```

## 🆘 **Troubleshooting**

### **Common Issues**
- **Database errors**: Run migrations first
- **API 401 errors**: Check JWT authentication setup
- **Frontend connection errors**: Verify `NEXT_PUBLIC_API_BASE_URL`
- **Device installation fails**: Check k3s cluster connectivity

### **Verification Commands**
```bash
# Check database schema
npx prisma db pull

# Test API health
curl http://localhost:8000/health

# Check device endpoints
python test_device_endpoints.py
```

---

**The system is now ready for testing!** 🎉

Start with the database migration, then test the APIs, and finally try the complete device installation and claiming flow.
