from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    Collection, UserStreak, RarityScore, UserAchievement,
    RecentActivity, BirdCategory
)

class CollectionService:
    @staticmethod
    def update_user_stats(user):
        """Update user's collection statistics"""
        # Update rarity counts
        rarity_score, _ = RarityScore.objects.get_or_create(user=user)
        
        collections = Collection.objects.filter(user=user)
        rarity_counts = collections.values('bird__rarity').annotate(
            count=Count('bird__rarity')
        )
        
        # Reset counts
        rarity_score.s_rarity_count = 0
        rarity_score.a_rarity_count = 0
        rarity_score.b_rarity_count = 0
        rarity_score.c_rarity_count = 0
        
        # Update counts
        for count in rarity_counts:
            rarity = count['bird__rarity']
            count_value = count['count']
            
            if rarity == 'S':
                rarity_score.s_rarity_count = count_value
            elif rarity == 'A':
                rarity_score.a_rarity_count = count_value
            elif rarity == 'B':
                rarity_score.b_rarity_count = count_value
            elif rarity == 'C':
                rarity_score.c_rarity_count = count_value
        
        rarity_score.calculate_total_score()
        rarity_score.save()
        
        return rarity_score

    @staticmethod
    def update_user_streak(user):
        """Update user's activity streak"""
        streak, _ = UserStreak.objects.get_or_create(user=user)
        today = timezone.now().date()
        
        if not streak.last_activity_date:
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.last_activity_date = today
        else:
            days_diff = (today - streak.last_activity_date).days
            
            if days_diff == 1:  # Consecutive day
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            elif days_diff > 1:  # Streak broken
                streak.current_streak = 1
            # If days_diff == 0, same day activity, no streak update needed
            
            streak.last_activity_date = today
        
        streak.save()
        return streak

    @staticmethod
    def check_and_award_achievements(user):
        """Check and award new achievements"""
        achievements = []
        
        # Get user stats
        collection_count = Collection.objects.filter(user=user).count()
        rarity_score = RarityScore.objects.get(user=user)
        streak = UserStreak.objects.get(user=user)
        locations = Collection.objects.filter(user=user).values('location').distinct().count()
        
        # Collection milestones
        milestones = [10, 50, 100, 500, 1000]
        for milestone in milestones:
            if collection_count >= milestone:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement_type='COLLECTION',
                    title=f'Collection Master {milestone}',
                    defaults={
                        'description': f'Collected {milestone} different bird species',
                        'value': milestone
                    }
                )
                if created:
                    achievements.append(achievement)
        
        # Rarity achievements
        if rarity_score.s_rarity_count > 0:
            achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement_type='RAREST',
                title='S-Rank Collector',
                defaults={
                    'description': 'Found an S-Rank rarity bird',
                    'value': rarity_score.s_rarity_count
                }
            )
            if created:
                achievements.append(achievement)
        
        # Streak achievements
        streak_milestones = [7, 30, 100, 365]
        for milestone in streak_milestones:
            if streak.longest_streak >= milestone:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement_type='STREAK',
                    title=f'{milestone} Day Streak',
                    defaults={
                        'description': f'Maintained a {milestone} day activity streak',
                        'value': milestone
                    }
                )
                if created:
                    achievements.append(achievement)
        
        # Location achievements
        location_milestones = [5, 10, 50, 100]
        for milestone in location_milestones:
            if locations >= milestone:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement_type='LOCATION',
                    title=f'Explorer {milestone}',
                    defaults={
                        'description': f'Explored {milestone} different locations',
                        'value': milestone
                    }
                )
                if created:
                    achievements.append(achievement)
        
        return achievements

    @staticmethod
    def get_collection_stats(user):
        """Get comprehensive collection statistics"""
        collections = Collection.objects.filter(user=user)
        
        return {
            'total_birds': collections.count(),
            'favorite_birds': collections.filter(is_favorite=True).count(),
            'featured_birds': collections.filter(is_featured=True).count(),
            'locations_explored': collections.values('location').distinct().count(),
            'rarity_distribution': RarityScore.objects.get(user=user),
            'recent_additions': RecentActivity.objects.filter(
                user=user,
                activity_type='added_to_collection'
            )[:5]
        }

    @staticmethod
    def get_bragging_rights(user):
        """Get user's bragging rights information"""
        rarity_score = RarityScore.objects.get(user=user)
        streak = UserStreak.objects.get(user=user)
        
        # Calculate rarest find percentile (simplified version)
        total_users = RarityScore.objects.count()
        users_below = RarityScore.objects.filter(
            total_score__lt=rarity_score.total_score
        ).count()
        percentile = (users_below / total_users) * 100
        
        return {
            'rarest_find': f"Top {int(percentile)}% Find",
            'collection_rank': f"Top {int(percentile)}%",
            'locations_explored': Collection.objects.filter(user=user).values(
                'location'
            ).distinct().count(),
            'streak_status': f"{streak.current_streak} Days Active",
            'achievements': UserAchievement.objects.filter(user=user)
        }

    @staticmethod
    def search_collection(user, search_params):
        """Search user's collection with filters"""
        collections = Collection.objects.filter(user=user)
        
        if search_params.get('query'):
            collections = collections.filter(
                Q(bird__name__icontains=search_params['query']) |
                Q(bird__scientific_name__icontains=search_params['query'])
            )
        
        if search_params.get('rarity'):
            collections = collections.filter(bird__rarity=search_params['rarity'])
        
        if search_params.get('category'):
            collections = collections.filter(
                bird__categorybird__category__name=search_params['category']
            )
        
        if search_params.get('location'):
            collections = collections.filter(
                location__icontains=search_params['location']
            )
        
        if search_params.get('date_from'):
            collections = collections.filter(
                date_added__gte=search_params['date_from']
            )
        
        if search_params.get('date_to'):
            collections = collections.filter(
                date_added__lte=search_params['date_to']
            )
        
        return collections

    @staticmethod
    def filter_collection(user, filter_type, filter_value):
        """Filter user's collection by specific criteria"""
        collections = Collection.objects.filter(user=user)
        
        if filter_type == 'rarity':
            collections = collections.filter(bird__rarity=filter_value)
        elif filter_type == 'region':
            collections = collections.filter(
                Q(location__icontains=filter_value) |
                Q(bird__global_distribution__icontains=filter_value)
            )
        elif filter_type == 'season':
            # This is a simplified version. You might want to implement
            # more sophisticated seasonal filtering based on your needs
            collections = collections.filter(
                bird__migration_pattern__icontains=filter_value
            )
        
        return collections 