import unittest
from pygame import Rect
from AutoChessEngine import RectCollider
import random


class RectColliderTests(unittest.TestCase):
    def test_collision_with_same_rect(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(0, 0), size=(2, 2))
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_overlapping_rect(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(1, 1), size=(2, 2))
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_non_overlapping_rect(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(3, 3), size=(2, 2))
        self.assertFalse(collider1.check_collision(collider2))

    def test_collision_with_rotated_rect(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(0, 0), size=(2, 2), angle=45)
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_non_overlapping_rotated_rect(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(3, 3), size=(2, 2), angle=45)
        self.assertFalse(collider1.check_collision(collider2))

    def test_collision_with_touching_edges(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(2, 0), size=(2, 2))
        self.assertFalse(collider1.check_collision(collider2))

    def test_collision_with_different_sizes(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(0, 0), size=(3, 3))
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_different_angles(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2), angle=30)
        collider2 = RectCollider(center=(0, 0), size=(2, 2), angle=60)
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_rect_inside_another(self):
        collider1 = RectCollider(center=(0, 0), size=(4, 4))
        collider2 = RectCollider(center=(0, 0), size=(2, 2))
        self.assertTrue(collider1.check_collision(collider2))

    def test_collision_with_rect_far_apart(self):
        collider1 = RectCollider(center=(0, 0), size=(2, 2))
        collider2 = RectCollider(center=(10, 10), size=(2, 2))
        self.assertFalse(collider1.check_collision(collider2))

    # Add more test cases here...

    def test_random_collision(self):
        for _ in range(10):
            size1 = (random.randint(1, 10), random.randint(1, 10))
            size2 = (random.randint(1, 10), random.randint(1, 10))
            center1 = (random.randint(-10, 10), random.randint(-10, 10))
            center2 = (random.randint(-10, 10), random.randint(-10, 10))
            angle1 = random.randint(0, 360)
            angle2 = random.randint(0, 360)

            collider1 = RectCollider(center=center1, size=size1, angle=angle1)
            collider2 = RectCollider(center=center2, size=size2, angle=angle2)

            expected_collision = self.check_collision_manually(collider1, collider2)
            actual_collision = collider1.check_collision(collider2)

            self.assertEqual(actual_collision, expected_collision)

    def check_collision_manually(self, collider1, collider2):
        # Manually check collision between two rectangles
        vertices1 = collider1.get_vertices()
        vertices2 = collider2.get_vertices()

        for axis in collider1._get_obb_axes() + collider2._get_obb_axes():
            if not collider1._overlap_on_axis(collider2, axis):
                return False

        return True


if __name__ == '__main__':
    unittest.main()