from django.db import models
from django.urls import reverse, NoReverseMatch


class Menu(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text='Internal name of the menu')

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(
        Menu,
        related_name='items',
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=200,
    )
    url = models.CharField(
        max_length=500,
        blank=True,
        help_text='Absolute or relative URL (e.g. /about/). Leave blank if using named_url.',
    )
    named_url = models.CharField(
        max_length=200,
        blank=True,
        help_text='Named URL (reverse name) e.g. "app:view_name"')
    order = (models.IntegerField(
        default=0,
        help_text='Order among siblings')
    )

    class Meta:
        verbose_name = 'Menu item'
        verbose_name_plural = 'Menu items'
        ordering = (
            'menu',
            'parent_id',
            'order',
            'id',
        )

    def __str__(self):
        return self.title

    def resolved_url(self):
        """
        Try to resolve named_url to path; fall back to url if provided.
        Note: reverse may raise NoReverseMatch — caller should handle.
        """
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.url or '#'
        return self.url or '#'
