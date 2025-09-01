"""
Test script to verify the emergency management system setup
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_dirs = [
        "src",
        "src/api",
        "src/data",
        "src/models",
        "config",
        "data",
        "data/models",
        "logs",
        "notebooks"
    ]
    
    required_files = [
        "requirements.txt",
        ".env.example",
        "config/settings.py",
        "src/api/main.py",
        "src/data/models.py",
        "notebooks/Simple_Emergency_Training.ipynb"
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_good = False
    
    return all_good

def test_api_import():
    """Test if the API can be imported"""
    print("\n🚀 Testing API import...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from src.api.main import app
        print("✅ API imported successfully")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

def test_models_import():
    """Test if data models can be imported"""
    print("\n📊 Testing data models import...")
    
    try:
        from src.data.models import Event, Emergency, Resource, Sensor
        print("✅ Data models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Data models import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Emergency Management System - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Data Models", test_models_import),
        ("API Import", test_api_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your setup is ready!")
        print("\nNext steps:")
        print("1. 📚 Upload 'notebooks/Simple_Emergency_Training.ipynb' to Google Colab")
        print("2. 🏃‍♂️ Run the notebook to train ML models")
        print("3. 📥 Download trained models to 'data/models/' directory")
        print("4. 🚀 Start the API server with: python test_server.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()
