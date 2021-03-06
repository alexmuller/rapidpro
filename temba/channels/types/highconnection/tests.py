from __future__ import unicode_literals, absolute_import

from django.urls import reverse
from temba.tests import TembaTest
from ...models import Channel


class HighConnectionTypeTest(TembaTest):

    def test_claim(self):
        Channel.objects.all().delete()

        url = reverse('channels.claim_high_connection')

        self.login(self.admin)

        response = self.client.get(reverse('channels.channel_claim'))
        self.assertNotContains(response, url)

        self.org.timezone = "Europe/Paris"
        self.org.save()

        # check that claim page URL appears on claim list page
        response = self.client.get(reverse('channels.channel_claim'))
        self.assertContains(response, url)

        # try to claim a channel
        response = self.client.get(url)
        post_data = response.context['form'].initial

        post_data['username'] = 'uname'
        post_data['password'] = 'pword'
        post_data['number'] = '5151'
        post_data['country'] = 'FR'

        response = self.client.post(url, post_data)

        channel = Channel.objects.get()

        self.assertEquals('FR', channel.country)
        self.assertTrue(channel.uuid)
        self.assertEquals(post_data['number'], channel.address)
        self.assertEquals(post_data['username'], channel.config_json()['username'])
        self.assertEquals(post_data['password'], channel.config_json()['password'])
        self.assertEquals('HX', channel.channel_type)

        config_url = reverse('channels.channel_configuration', args=[channel.pk])
        self.assertRedirect(response, config_url)

        response = self.client.get(config_url)
        self.assertEquals(200, response.status_code)

        self.assertContains(response, reverse('courier.hx', args=[channel.uuid, 'receive']))
