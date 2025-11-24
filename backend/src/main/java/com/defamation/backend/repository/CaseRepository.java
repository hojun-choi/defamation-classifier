package com.defamation.backend.repository;

import com.defamation.backend.domain.Case;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

public interface CaseRepository extends JpaRepository<Case, Long> {

    /**
     * 실제 판례 검색/페이징
     * is_deleted = false 만
     */
    @Query("""
        SELECT c FROM Case c
        WHERE c.isDeleted = false
          AND (
            :q IS NULL OR :q = '' OR
            c.problemSituation LIKE %:q% OR
            c.defendant LIKE %:q% OR
            c.caseNames LIKE %:q%
          )
        ORDER BY c.createdAt DESC
    """)
    Page<Case> search(@Param("q") String q, Pageable pageable);
}
