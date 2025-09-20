from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Project, Category, Membership, RoleType


class ProjectAPITestCase(APITestCase):
    """
    Test case for Project API endpoints.
    Tests authentication, data creation, and API responses.
    """
    
    def setUp(self):
        """Set up test data including users, categories, and projects."""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpassword123'
        )
        
        # Create test categories
        self.parent_category = Category.objects.create(
            name='Technology'
        )
        self.child_category = Category.objects.create(
            name='Web Development',
            parent=self.parent_category
        )
        self.standalone_category = Category.objects.create(
            name='Marketing'
        )
        
        # Create test projects
        self.project1 = Project.objects.create(
            title='E-commerce Platform',
            description='Building a modern e-commerce platform with Django and React',
            category=self.child_category
        )
        self.project2 = Project.objects.create(
            title='Marketing Campaign',
            description='Q4 marketing campaign for product launch',
            category=self.standalone_category
        )
        self.project3 = Project.objects.create(
            title='Mobile App Development',
            description='Cross-platform mobile app using React Native',
            category=self.child_category
        )
        
        # Create memberships (user-project relationships)
        Membership.objects.create(
            person=self.user1,
            project=self.project1,
            role=RoleType.OWNER
        )
        Membership.objects.create(
            person=self.user2,
            project=self.project1,
            role=RoleType.MEMBER
        )
        Membership.objects.create(
            person=self.user1,
            project=self.project2,
            role=RoleType.MEMBER
        )
        Membership.objects.create(
            person=self.user2,
            project=self.project3,
            role=RoleType.OWNER
        )
        
        # Set up API client
        self.client = APIClient()
        self.projects_url = reverse('projects')
    
    def test_projects_api_requires_authentication(self):
        """Test that the projects API requires authentication."""
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_projects_api_with_authentication(self):
        """Test that authenticated users can access the projects API."""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # for mm in Membership.objects.filter(person=self.user1):
        #     print(mm.project.title)
        #     for i in mm.project.members.all():
        #         print('      ', i.username, i.id)
        print(response.data)
        # Check that we get a list of projects
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)  # We created 3 projects
    
    def test_projects_api_response_structure(self):
        """Test the structure of the API response."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check first project structure
        first_project = response.data[0]
        expected_fields = ['title', 'description', 'category', 'members', 'created_at', 'updated_at']
        
        for field in expected_fields:
            self.assertIn(field, first_project)
        
        # Check that members field contains member IDs
        self.assertIsInstance(first_project['members'], list)
    
    def test_projects_ordered_by_updated_at_desc(self):
        """Test that projects are ordered by updated_at in descending order."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that projects are ordered by updated_at (most recent first)
        projects = response.data
        for i in range(len(projects) - 1):
            current_updated = projects[i]['updated_at']
            next_updated = projects[i + 1]['updated_at']
            self.assertGreaterEqual(current_updated, next_updated)
    
    def test_project_members_serialization(self):
        """Test that project members are correctly serialized as membership IDs."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the e-commerce project in response
        ecommerce_project = None
        for project in response.data:
            if project['title'] == 'E-commerce Platform':
                ecommerce_project = project
                break
        
        self.assertIsNotNone(ecommerce_project)
        
        # Check that it has the correct number of members
        # Project1 has 2 memberships (user1 as owner, user2 as member)
        expected_membership_ids = list(
            Membership.objects.filter(project=self.project1).values_list('person_id', flat=True)
        )
        self.assertEqual(len(ecommerce_project['members']), 2)
        self.assertEqual(set(ecommerce_project['members']), set(expected_membership_ids))
    
    def test_different_user_sees_same_projects(self):
        """Test that different authenticated users see the same projects."""
        # Test with user1
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.get(self.projects_url)
        
        # Test with user2
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.get(self.projects_url)
        
        # Both should see the same projects (no filtering by user)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), len(response2.data))
        
        # Extract project titles for comparison
        titles1 = {project['title'] for project in response1.data}
        titles2 = {project['title'] for project in response2.data}
        self.assertEqual(titles1, titles2)
    
    def test_category_relationships(self):
        """Test that projects correctly reference their categories."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create a mapping of project titles to their expected category IDs
        expected_categories = {
            'E-commerce Platform': self.child_category.id,
            'Marketing Campaign': self.standalone_category.id,
            'Mobile App Development': self.child_category.id,
        }
        
        for project in response.data:
            expected_category_id = expected_categories[project['title']]
            self.assertEqual(project['category'], expected_category_id)
    
    def test_empty_projects_list(self):
        """Test API response when no projects exist."""
        # Delete all projects
        Project.objects.all().delete()
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
    
    def test_project_without_members(self):
        """Test serialization of project with no members."""
        # Create a project with no memberships
        project_no_members = Project.objects.create(
            title='Solo Project',
            description='A project with no team members',
            category=self.standalone_category
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the solo project
        solo_project = None
        for project in response.data:
            if project['title'] == 'Solo Project':
                solo_project = project
                break
        
        self.assertIsNotNone(solo_project)
        self.assertEqual(solo_project['members'], [])


class ModelsTestCase(TestCase):
    """Test case for model functionality and relationships."""
    
    def setUp(self):
        """Set up test data for model tests."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Test Category')
        
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            category=self.category
        )
    
    def test_category_str_representation(self):
        """Test Category model string representation."""
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_project_str_representation(self):
        """Test Project model string representation."""
        self.assertEqual(str(self.project), 'Test Project')
    
    def test_membership_creation_and_str_representation(self):
        """Test Membership model creation and string representation."""
        membership = Membership.objects.create(
            person=self.user,
            project=self.project,
            role=RoleType.OWNER
        )
        
        expected_str = f"{self.user.username} - {self.project.title}"
        self.assertEqual(str(membership), expected_str)
        self.assertEqual(membership.role, RoleType.OWNER)
    
    def test_membership_unique_constraint(self):
        """Test that a user cannot have multiple memberships for the same project."""
        # Create first membership
        Membership.objects.create(
            person=self.user,
            project=self.project,
            role=RoleType.MEMBER
        )
        
        # Try to create duplicate membership
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.user,
                project=self.project,
                role=RoleType.OWNER
            )
    
    def test_category_parent_relationship(self):
        """Test Category parent-child relationship."""
        parent_category = Category.objects.create(name='Parent')
        child_category = Category.objects.create(name='Child', parent=parent_category)
        
        self.assertEqual(child_category.parent, parent_category)
        self.assertIsNone(parent_category.parent)
    
    def test_project_timestamps(self):
        """Test that project timestamps are automatically set."""
        project = Project.objects.create(
            title='Timestamp Test',
            description='Testing timestamps',
            category=self.category
        )
        
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)
        
        # Check that updated_at changes when we save
        original_updated = project.updated_at
        project.title = 'Updated Title'
        project.save()
        
        self.assertGreater(project.updated_at, original_updated)
