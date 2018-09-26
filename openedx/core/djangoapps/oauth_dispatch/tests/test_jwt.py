"""Tests covering JWT construction utilities."""
import ddt
import jwt
from django.test import TestCase

from openedx.core.djangoapps.oauth_dispatch.tests import mixins
from openedx.core.lib.token_utils import JwtBuilder
from student.tests.factories import UserFactory, UserProfileFactory


@ddt.ddt
class TestJwtBuilder(mixins.AccessTokenMixin, TestCase):
    """
    Test class for JwtBuilder.
    """

    expires_in = 10
    shard = 2

    def setUp(self):
        super(TestJwtBuilder, self).setUp()

        self.user = UserFactory()
        self.profile = UserProfileFactory(user=self.user)
        self.scopes = ['email', 'profile']

    def test_jwt_construction(self):
        """
        Verify that a valid JWT is built, including claims for the requested scopes.
        """
        token = JwtBuilder(self.user).build_token(expires_in=self.expires_in)
        self.assert_valid_jwt_access_token(token, self.user, self.scopes)

    def test_user_profile_missing(self):
        """
        Verify that token construction succeeds if the UserProfile is missing.
        """
        self.profile.delete()

        token = JwtBuilder(self.user).build_token(expires_in=self.expires_in)
        self.assert_valid_jwt_access_token(token, self.user, self.scopes)

    def test_override_secret_and_audience(self):
        """
        Verify that the signing key and audience can be overridden.
        """
        secret = 'avoid-this'
        audience = 'avoid-this-too'

        token = JwtBuilder(
            self.user,
            secret=secret,
        ).build_token(
            expires_in=self.expires_in,
            aud=audience,
        )

        jwt.decode(token, secret, audience=audience)
