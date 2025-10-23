# tests/test_api_endpoints.py
import requests
import json
from datetime import datetime

class EuropeanMappingAPITester:
    def __init__(self, base_url='http://localhost:8002'):
        self.base_url = base_url
        self.session = requests.Session()

    def test_server_connectivity(self):
        """Test if the Django server is running"""
        print("🔗 Testing server connectivity...")
        try:
            response = self.session.get(self.base_url, timeout=5)
            print(f"✅ Server accessible: HTTP {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not accessible: {e}")
            return False

    def test_cities_endpoint(self):
        """Test cities API endpoint"""
        print("\n🏙️ Testing Cities Endpoint...")

        try:
            response = self.session.get(f'{self.base_url}/api/cities/')
            print(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ Expected 200, got {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

            # Check if it's a proper GeoJSON FeatureCollection
            if not isinstance(data, dict):
                print("❌ Response is not a JSON object")
                return False

            if data.get('type') != 'FeatureCollection':
                print(f"❌ Expected 'FeatureCollection', got '{data.get('type')}'")
                return False

            features = data.get('features', [])
            print(f"Number of features: {len(features)}")

            if len(features) == 0:
                print("⚠️  No cities found in database - this might be expected if no data has been loaded")
                return True  # Not a failure if no data exists

            # Test first feature structure
            feature = features[0]
            required_keys = ['type', 'geometry', 'properties']

            for key in required_keys:
                if key not in feature:
                    print(f"❌ Missing required key: {key}")
                    return False

            # Check geometry
            geom = feature['geometry']
            if geom['type'] != 'Point':
                print(f"❌ Expected Point geometry, got {geom['type']}")
                return False

            if not isinstance(geom['coordinates'], list) or len(geom['coordinates']) != 2:
                print(f"❌ Invalid coordinates: {geom['coordinates']}")
                return False

            # Check properties
            props = feature['properties']
            required_props = ['name', 'country', 'population']

            for prop in required_props:
                if prop not in props:
                    print(f"❌ Missing required property: {prop}")
                    return False

            print(f"✅ Cities endpoint working correctly")
            print(f"Sample city: {props['name']}, {props['country']} (Pop: {props['population']:,})")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def test_regions_endpoint(self):
        """Test regions API endpoint"""
        print("\n🗺️ Testing Regions Endpoint...")

        try:
            response = self.session.get(f'{self.base_url}/api/regions/')
            print(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ Expected 200, got {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

            data = response.json()
            print(f"Response type: {type(data)}")

            if not isinstance(data, dict):
                print("❌ Response is not a JSON object")
                return False

            if data.get('type') != 'FeatureCollection':
                print(f"❌ Expected 'FeatureCollection', got '{data.get('type')}'")
                return False

            features = data.get('features', [])
            print(f"Number of features: {len(features)}")

            if len(features) == 0:
                print("⚠️  No regions found in database - this might be expected if no data has been loaded")
                return True

            # Test first feature
            feature = features[0]
            props = feature['properties']

            print(f"✅ Regions endpoint working correctly")
            print(f"Sample region: {props.get('name', 'Unknown')}, {props.get('country', 'Unknown')}")
            return True

        except Exception as e:
            print(f"❌ Error testing regions: {e}")
            return False

    def test_statistics_endpoints(self):
        """Test statistics endpoints"""
        print("\n📊 Testing Statistics Endpoints...")

        endpoints = [
            '/api/cities/statistics/',
            '/api/regions/statistics/'
        ]

        success = True
        for endpoint in endpoints:
            try:
                response = self.session.get(f'{self.base_url}{endpoint}')
                print(f"{endpoint}: HTTP {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"  Stats keys: {list(data.keys())}")
                else:
                    print(f"  ❌ Failed: {response.text[:200]}")
                    success = False

            except Exception as e:
                print(f"  ❌ Error: {e}")
                success = False

        return success

    def test_filtering(self):
        """Test filtering functionality"""
        print("\n🔍 Testing Filtering...")

        # Test city filters
        test_filters = [
            ('population_min=100000', 'Population filter'),
            ('country=Germany', 'Country filter'),
            ('city_type=capital', 'City type filter')
        ]

        for filter_param, description in test_filters:
            try:
                url = f'{self.base_url}/api/cities/?{filter_param}'
                response = self.session.get(url)

                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('features', []))
                    print(f"✅ {description}: {count} results")
                else:
                    print(f"❌ {description} failed: HTTP {response.status_code}")

            except Exception as e:
                print(f"❌ {description} error: {e}")

        return True

    def test_welcome_endpoint(self):
        """Test the welcome endpoint"""
        print("\n👋 Testing Welcome Endpoint...")

        try:
            response = self.session.get(f'{self.base_url}/api/cities/welcome/')
            print(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ Expected 200, got {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

            data = response.json()
            print(f"Response: {data}")

            # Check if response has the expected message
            if not isinstance(data, dict):
                print("❌ Response is not a JSON object")
                return False

            if 'message' not in data:
                print("❌ Missing 'message' key in response")
                return False

            expected_message = "Welcome to the European Mapping API Service!"
            if data['message'] != expected_message:
                print(f"❌ Expected message '{expected_message}', got '{data['message']}'")
                return False

            print("✅ Welcome endpoint working correctly")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting European Mapping API Tests")
        print("=" * 50)

        # Test server connectivity first
        if not self.test_server_connectivity():
            print("❌ Server not accessible. Make sure Django is running: python manage.py runserver")
            return False

        results = {
            'cities': self.test_cities_endpoint(),
            'regions': self.test_regions_endpoint(),
            'statistics': self.test_statistics_endpoints(),
            'filtering': self.test_filtering(),
            'welcome': self.test_welcome_endpoint()
        }

        print("\n" + "=" * 50)
        print("📋 Test Results Summary:")

        passed = sum(results.values())
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name.title()}: {status}")

        print(f"\n🎯 Overall: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("🔧 Some tests failed. Check the output above for details.")

        return passed == total

# Run tests
if __name__ == "__main__":
    tester = EuropeanMappingAPITester()
    tester.run_all_tests()